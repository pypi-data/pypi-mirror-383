import os
import json
import tempfile
import re
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from .config import MainConfig
from .config.program import Program
from .config.image import ImageBuild, DEFAULT_DUMP_IMAGE_STORE
from .shared import log, run_shell, file_hash, ensure_home_dir_special_prefix, KV
from .exceptions import SandboxExecution

VOL_LABEL_CREATED_BY = "created_by.sandock"
VOL_SANDBOX_DIR_SUFFIX_NAME = "sandock-dir-"
VOL_DIR_SUBS = "${VOL_DIR}"
CONTAINER_STATE_RUNNING = "running"
special_char_re = re.compile(r"\W+")


class SandboxExec(object):
    name: str
    cfg: MainConfig
    program: Program
    container_name: str

    def __init__(
        self, name: str, program: Program, cfg: MainConfig
    ) -> None:
        self.name = name
        self.cfg = cfg
        self.program = program

        # prevent if it's run on homedir, we don't want unintended breach except their aware
        if (
            self.program.sandbox_mount.enable
            and not self.program.allow_home_dir
            and self.current_dir == self.home_dir
        ):
            raise SandboxExecution(
                "cannot be ran on top of home directory when the program's sandbox mount is enabled"
            )

        self.container_name = self.generate_container_name()

    def hook_recreate_img(self, execute: bool=False) -> None:
        """
        register for pre-exec cmd to delete image run the related container
        """
        if not execute:
            return

        log.debug("[hook] registring for image deletion: {self.program.image}")
        self.program.pre_exec_cmds.insert(0, " ".join([
            self.docker_bin, "image", "rm", self.program.image
        ]))

    @property
    def docker_bin(self) -> str:
        default_bin = self.cfg.execution.docker_bin
        custom_executor = self.program.executor
        if not custom_executor:
            return default_bin

        executor = self.cfg.executors.get(custom_executor)
        if not executor:
            raise SandboxExecution(f"Executor `{custom_executor}` is not defined")

        return executor.bin_path if executor.bin_path else default_bin

    @property
    def current_timestamp(self) -> float:
        return datetime.now().timestamp()

    def generate_container_name(self) -> str:
        if self.program.name:
            return self.program.name

        generated_name = f"{self.cfg.execution.container_name_prefix}{self.name}"
        # don't give timestampt if it's persist
        if not self.program.persist.enable:
            generated_name += f"-{self.current_timestamp}"
        return generated_name

    @property
    def home_dir(self) -> Optional[str]:
        return os.environ.get("HOME")

    @property
    def current_dir(self) -> str:
        return os.getcwd()

    @property
    def exec_path(self) -> str:
        """
        grab the alias first
        """
        pe = self.program.exec
        return self.program.aliases.get(pe, pe)

    def run_container_cmd(self) -> List[str]:
        """
        container run command builder
        """
        command = [
            self.docker_bin,
            "run",
            "--entrypoint",
            self.exec_path,
            "--name",
            self.container_name,
        ]

        if not self.program.persist.enable:
            command.append("--rm")

        if self.program.interactive:
            command.append("-it")

        if self.program.platform:
            command.extend(["--platform", self.program.platform])

        if self.program.hostname:
            command.extend(["--hostname", self.program.hostname])

        if self.program.network:
            command.extend(["--network", self.program.network])

        user = self.program.user
        if user:
            uid = self.current_uid if user.keep_id else user.uid
            gid = self.current_gid if user.keep_id else user.gid
            command.extend(["-u", f"{uid}:{gid}"])

        workdir = self.program.workdir
        volumes = self.program.volumes
        if self.program.sandbox_mount.enable:
            # when sandbox mount enable, set the default workdir to it
            workdir = self.program.sandbox_mount.current_dir_mount
            sandbox_mount = (
                f"{self.current_dir}:{self.program.sandbox_mount.current_dir_mount}"
            )
            if self.program.sandbox_mount.read_only:
                sandbox_mount += ":ro"

            volumes.append(sandbox_mount)

        for v in volumes:
            if VOL_DIR_SUBS in v:
                log.debug("[vol] volume dir identified, subs the var")
                v = v.replace(
                    VOL_DIR_SUBS, special_char_re.sub("_", self.current_dir[1:])
                )
            command.extend(["-v", v])

        if workdir:
            command.extend(["--workdir", workdir])

        command.extend([f"-e {k}='{v}'" for k, v in self.program.env.items()])
        command.extend([f"-p {p}" for p in self.program.ports])
        command.extend([f"--cap-add={c}" for c in self.program.cap_add])
        command.extend([f"--cap-drop={c}" for c in self.program.cap_drop])
        command.extend(self.program.extra_run_args)
        command.append(self.program.image)

        return command

    @property
    def current_uid(self) -> int:
        return os.getuid()

    @property
    def current_gid(self) -> int:
        return os.getgid()

    def ensure_volume(self, name: str) -> None:
        """
        ensure the volume created as expected based on configuration if exists
        """
        log.debug(f"[vol] check volume by name {name} in configuration")
        vol = self.cfg.volumes.get(name)
        if not vol:
            log.debug(f"[vol] {name} not exists in config")
            return

        inspect_vol = run_shell(
            f"{self.docker_bin} volume inspect {name}", check_err=False
        )
        # vol exists
        if inspect_vol.returncode == 0:
            vol_info = json.loads(inspect_vol.stdout)
            log.debug(f"[vol] exists, info ~> {vol_info}")
            return

        log.info(f"[vol] creating vol {name}")
        # mandatory label
        if VOL_LABEL_CREATED_BY not in vol.labels:
            vol.labels[VOL_LABEL_CREATED_BY] = "true"

        vol_create_cmd = [f"{self.docker_bin} volume create"]

        if vol.driver:
            vol_create_cmd.append(f"--driver={vol.driver}")

        if vol.driver_opts:
            vol_create_cmd.append(" ".join([f"--opt {k}={v}" for k, v in vol.driver_opts.items()]))

        if vol.labels:
            vol_create_cmd.append(" ".join([f"--label {k}='{v}'" for k, v in vol.labels.items()]))

        vol_create_cmd.append(name)
        run_shell(vol_create_cmd, capture_output=False)

    def ensure_network(self) -> None:
        net_name = self.program.network
        if not net_name:
            return

        log.debug(f"[net] ensuring network by name `{net_name}` in configuration")
        network = self.cfg.networks.get(net_name)
        if not network:
            log.debug(
                f"[net] network by name {net_name} is not managed in configuration"
            )
            return

        inspect_net = run_shell(
            f"{self.docker_bin} network inspect {net_name}", check_err=False
        )
        if inspect_net.returncode == 0:
            net_info = json.loads(inspect_net.stdout)
            log.debug(f"[net] exists, info ~> {net_info}")
            return

        log.info(f"[net] creating net {net_name}")

        net_params = " ".join([f"--{k}={v}" for k, v in network.params.items()])
        net_driver_opts = " ".join(
            [f"--opt {k}={v}" for k, v in network.driver_opts.items()]
        )
        net_create_cmd = (
            f"{self.docker_bin} network create "
            f"--driver={network.driver} {net_params} {net_driver_opts}"
            f"{net_name}"
        )
        run_shell(net_create_cmd, capture_output=False)

    def custom_image_dockerfile_store(
        self, path: str, image_name: str, build: ImageBuild
    ) -> Path:
        docker_file_hash = file_hash(fpath=path, max_chars=20)
        return Path(
            (
                ensure_home_dir_special_prefix(path=build.dump.store)
                .replace("${image}", image_name)
                .replace("${hash}", docker_file_hash)
                .replace(
                    "${platform}",
                    (
                        ""
                        if not self.program.platform
                        else self.program.platform.replace("/", "_")
                    ),
                )
            )
        )

    def ensure_custom_image(self, image_name: Optional[str] = None) -> None:
        """
        if it's intended to use custom image
        """
        image_name = image_name or self.program.image
        build_image = self.cfg.images.get(image_name) or self.program.build
        if not build_image:
            return

        # recursively check for any dependent before build
        if build_image.depends_on:
            log.debug(f"found image depends on {build_image.depends_on}")
            self.ensure_custom_image(image_name=build_image.depends_on)

        inspect_img = run_shell(
            f"{self.docker_bin} image inspect {image_name}", check_err=False
        )

        if inspect_img.returncode == 0:
            img_info = json.loads(inspect_img.stdout)
            log.debug(f"[img] exists, info ~> {img_info}")
            return

        log.info(f"[img] creating image {image_name}")
        working_dir = build_image.context
        if not working_dir:
            # if context not set then create the temporary one
            log.debug("[img] context was not set, create the temporary dir")
            working_dir = tempfile.mkdtemp()
        else:
            working_dir = ensure_home_dir_special_prefix(path=working_dir)

        docker_file_path = build_image.dockerFile
        if not docker_file_path and build_image.dockerfile_inline:
            log.debug(
                "[img] docker file not defined, create the temporary one from `dockerfile_inline`"
            )
            docker_file_path = tempfile.mktemp()
            with open(docker_file_path, "w") as fh:
                fh.write(
                    build_image.dockerfile_inline.replace(
                        "{CURRENT_GID}", str(self.current_gid)
                    ).replace("{CURRENT_UID}", str(self.current_uid))
                )

        docker_file_path = ensure_home_dir_special_prefix(path=docker_file_path)  # type: ignore[arg-type]

        # if dumped image enabled and found then just load from it and skip image building
        dump_store_path = self.custom_image_dockerfile_store(
            path=docker_file_path, image_name=image_name, build=build_image
        )
        if build_image.dump.enable and dump_store_path.exists():
            log.info(
                f"[img] image dump is enable and cache image found, will restore the image from file `{dump_store_path}`"
            )
            image_restore_cmd = f"{self.docker_bin} image load -i {dump_store_path}"
            run_shell(image_restore_cmd, capture_output=False)
            return

        img_create_cmd = f"{self.docker_bin} build -t {image_name}"
        if docker_file_path:
            img_create_cmd += f" -f {docker_file_path}"

        for k_arg, v_arg in build_image.args.items():
            img_create_cmd += f' --build-arg {k_arg}="{v_arg}"'

        if build_image.extra_build_args:
            img_create_cmd += f' {" ".join(build_image.extra_build_args)}'

        if self.program.platform:
            img_create_cmd += f" --platform={self.program.platform}"

        img_create_cmd += f" {working_dir}"
        run_shell(img_create_cmd, capture_output=False)

        # dump image if it's enabled
        if build_image.dump.enable and not dump_store_path.exists():
            # clean up previous one
            if dump_store_path.parent.exists() and build_image.dump.cleanup_prev:
                log.info("[img] cleanup previous dumped image")
                base_store = os.path.basename(build_image.dump.store)

                # if using other than known format then just ignore it
                if base_store == os.path.basename(DEFAULT_DUMP_IMAGE_STORE):
                    for prev_img in dump_store_path.parent.glob(f"{image_name}*.tar"):
                        log.info(f"[img] cleanup previous cached image {prev_img}")
                        prev_img.unlink()
                else:
                    log.warning(
                        f"[img] it's using non standard pattern ({base_store}), cannot run cleanup operation"
                    )

            # ensure the parent directory is exists
            dump_store_path.parent.mkdir(parents=True, exist_ok=True)
            log.info(f"[img] save dumped image into {dump_store_path}")
            image_dump_cmd = (
                f"{self.docker_bin} image save {image_name} --output {dump_store_path}"
            )
            run_shell(image_dump_cmd, capture_output=False)

        # garbage collect
        if (
            build_image.dockerfile_inline
            and docker_file_path is not None
            and os.path.isfile(docker_file_path)
        ):
            os.remove(docker_file_path)

    def inspect_container_cmd(self) -> str:
        return f"{self.docker_bin} container inspect {self.container_name}"

    def container_start_cmd(self) -> str:
        return f"{self.docker_bin} container start {self.container_name}"

    def _check_running_container(self, container_info: List[KV]) -> bool:
        return bool(container_info[0].get("State", {}).get("Status") == CONTAINER_STATE_RUNNING)

    @property
    def attach_container(self) -> bool:
        """
        determine whether attaching to existsing container ?
        """
        if not self.program.persist.enable:
            return False

        inspect_result = run_shell(self.inspect_container_cmd(), check_err=False)
        if inspect_result.returncode != 0:
            # it might be the uncreated container
            err_msg = str(inspect_result.stderr)
            if "no such container" in err_msg.lower():
                return False

            # the known message if container not found, other than that just raise it
            raise SandboxExecution(f"error during check container status: {err_msg}")

        container_info = json.loads(inspect_result.stdout)
        if len(container_info) < 1:
            log.warning(
                f"empty container info status during inspection ~> {container_info}"
            )
            return False

        is_running = self._check_running_container(container_info)
        if not is_running and self.program.persist.auto_start:
            log.warning("persist container is down, starting container")
            run_shell(
                self.container_start_cmd(),
                capture_output=False,
            )

            # just attach to it after start
            return True

        return is_running

    def exec_container_cmd(self) -> List[str]:
        cmd = [self.docker_bin, "exec"]

        if self.program.interactive:
            cmd.append("-it")

        cmd.extend([self.container_name, self.exec_path])
        return cmd

    def do(self, args: List[str] = []) -> None:
        """
        main flows
        """
        for pre_exec in self.program.pre_exec_cmds:
            log.debug(f"[pre_exec] running shell command ~> {pre_exec}")
            run_shell(pre_exec)

        # ensure container dependencies are created
        self.ensure_custom_image()
        self.ensure_network()
        for extra_mount in self.program.volumes:
            vol = extra_mount.split(":")[0]
            self.ensure_volume(name=vol)

        run_container_cmd = (
            self.exec_container_cmd()
            if self.attach_container
            else self.run_container_cmd()
        )
        run_container_cmd.extend(args)

        log.debug(f"starting container cmd ~> {run_container_cmd}")
        run_shell(run_container_cmd, capture_output=False)
