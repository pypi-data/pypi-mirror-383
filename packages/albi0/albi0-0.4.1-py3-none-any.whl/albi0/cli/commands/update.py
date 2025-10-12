import os

import anyio
from asyncer import syncify
import click
from tqdm.asyncio import tqdm

from albi0.update import updaters
from albi0.utils import set_directory, timer


@click.command(help='更新资源清单并下载资源文件')
@click.option(
	'-w',
	'--working-dir',
	default=None,
	type=click.Path(exists=True, file_okay=False, writable=True),
)
@click.option(
	'-n',
	'--updater-name',
	type=str,
	help='更新器名称，支持传入更新器/组名',
)
@click.option(
	'-m',
	'--manifest-path',
	type=click.Path(dir_okay=False, writable=True),
	help='本地清单文件路径，如果未指定则使用更新器默认路径',
)
@click.option(
	'-s',
	'--semaphore-limit',
	'--max-workers',
	default=10,
	type=int,
	show_default=True,
)
@click.option(
	'--ignore-version',
	is_flag=True,
	default=False,
	help='忽略版本号检查，仅检查资源清单变化',
)
@click.option(
	'--version-only',
	is_flag=True,
	default=False,
	help='仅获取远程版本号，不下载资源文件',
)
@click.option(
	'--manifest-only',
	is_flag=True,
	default=False,
	help='仅更新资源清单，不下载资源文件',
)
@click.argument('patterns', nargs=-1, default=None)
@click.pass_context
@syncify
async def update(
	ctx: click.Context,
	patterns: list[str] | None,
	working_dir: str | None,
	updater_name: str,
	manifest_path: str | None,
	version_only: bool,
	manifest_only: bool,
	semaphore_limit: int,
	ignore_version: bool,
) -> None:
	patterns = patterns or []
	os.chdir(working_dir or './')
	updater_set = updaters.get_processors(updater_name)
	if not updater_set:
		click.echo(f'找不到输入的更新器/组：{updater_name}')
		return

	_updater_string = '找到以下更新器：\n'
	_updater_string += ''.join(
		[f'    {name}: {processor.desc}\n' for name, processor in updaters.items()]
	)
	click.echo(_updater_string)

	with (
		timer('✅ 更新完成~ 总耗时: {duration:.2f}s'),
		set_directory(working_dir or './'),
	):
		for updater in updater_set:
			# 如果指定了自定义清单路径，设置到版本管理器中
			if manifest_path:
				click.echo(f'使用自定义清单文件路径: {manifest_path}')
				updater.version_manager.local_manifest_path = manifest_path

			click.echo(f'运行更新器：{updater.name}')
			if version_only:
				click.echo(
					f'远程版本：{updater.version_manager.get_remote_version()}\n'
				)
				continue

			if manifest_only:
				continue

			click.echo(
				f'本地版本：{updater.version_manager.load_local_version() or "无"}\n'
				f'远程版本：{updater.version_manager.get_remote_version()}'
			)
			if not updater.version_manager.is_version_outdated and not ignore_version:
				click.echo('版本最新，无需更新。')
				continue

			click.echo('开始更新...')
			await updater.update(
				progress_bar=tqdm(desc='下载资源文件', unit='file'),
				patterns=patterns,
				semaphore=anyio.Semaphore(semaphore_limit),
			)
			click.echo(
				f'✅(<ゝω・)～☆更新完毕！'
				f'本地版本：{updater.version_manager.load_local_version() or "无"}\n'
			)
