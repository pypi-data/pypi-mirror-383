from pathlib import Path
from typing import Iterable

from ..easyrip_web.third_party_api import zhconvert
from .global_lang_val import (
    Lang_tag,
    Lang_tag_language,
    Lang_tag_region,
    Lang_tag_script,
)


def translate_subtitles(
    directory: Path,
    infix: str,
    target_lang: str | Lang_tag,
    *,
    file_intersection_selector: Iterable[Path] | None = None,
) -> list[tuple[Path, str]]:
    """
    #### 自动搜索符合中缀的字幕文件，翻译为目标语言
    文件交集选择器: 不为 None 时，与选择器有交集的 Path 才会选择
    Return: list[tuple[file, content]]
    """

    from ..easyrip_mlang import gettext
    from ..ripper.utils import read_text

    if isinstance(target_lang, str):
        target_lang_tag: Lang_tag = Lang_tag.from_str(target_lang)
    else:
        target_lang_tag = target_lang

    if file_intersection_selector is not None:
        file_intersection_selector = set(file_intersection_selector)

    file_list = list[tuple[Path, str]]()
    for f in directory.iterdir():
        if f.suffix not in {".ass", ".ssa", ".srt"} or (
            file_intersection_selector is not None
            and f not in file_intersection_selector
        ):
            continue

        if len(_stems := f.stem.split(".")) < 1:
            continue
        if infix == _stems[-1]:
            file_list.append(
                (
                    f.with_name(
                        f"{'.'.join(f.stem.split('.')[:-1])}.{target_lang_tag}{f.suffix}"
                    ),
                    read_text(f),
                )
            )

    match Lang_tag.from_str(infix):
        case (
            Lang_tag(
                language=Lang_tag_language.zh,
                script=Lang_tag_script.Hans,
                region=_,
            )
            | Lang_tag(
                language=Lang_tag_language.zh,
                script=_,
                region=Lang_tag_region.CN,
            )
        ):
            # 简体 -> 繁体
            match target_lang_tag:
                case Lang_tag(
                    language=Lang_tag_language.zh,
                    script=_,
                    region=Lang_tag_region.HK,
                ):
                    file_list = [
                        (
                            f[0],
                            zhconvert.translate(
                                org_text=f[1],
                                target_lang=zhconvert.Target_lang.HK,
                            ),
                        )
                        for f in file_list
                    ]

                case Lang_tag(
                    language=Lang_tag_language.zh,
                    script=_,
                    region=Lang_tag_region.TW,
                ):
                    file_list = [
                        (
                            f[0],
                            zhconvert.translate(
                                org_text=f[1],
                                target_lang=zhconvert.Target_lang.TW,
                            ),
                        )
                        for f in file_list
                    ]

                case Lang_tag(
                    language=Lang_tag_language.zh,
                    script=Lang_tag_script.Hant,
                    region=_,
                ):
                    file_list = [
                        (
                            f[0],
                            zhconvert.translate(
                                org_text=f[1],
                                target_lang=zhconvert.Target_lang.Hant,
                            ),
                        )
                        for f in file_list
                    ]

                case _:
                    raise Exception(
                        gettext("Unsupported language tag: {}").format(target_lang_tag)
                    )

        case (
            Lang_tag(
                language=Lang_tag_language.zh,
                script=Lang_tag_script.Hant,
                region=_,
            )
            | Lang_tag(
                language=Lang_tag_language.zh,
                script=_,
                region=Lang_tag_region.HK | Lang_tag_region.TW,
            )
        ):
            # 繁体 -> 简体
            match target_lang_tag:
                case Lang_tag(
                    language=Lang_tag_language.zh,
                    script=_,
                    region=Lang_tag_region.CN,
                ):
                    file_list = [
                        (
                            f[0],
                            zhconvert.translate(
                                org_text=f[1], target_lang=zhconvert.Target_lang.CN
                            ),
                        )
                        for f in file_list
                    ]

                case Lang_tag(
                    language=Lang_tag_language.zh,
                    script=Lang_tag_script.Hans,
                    region=_,
                ):
                    file_list = [
                        (
                            f[0],
                            zhconvert.translate(
                                org_text=f[1],
                                target_lang=zhconvert.Target_lang.Hans,
                            ),
                        )
                        for f in file_list
                    ]

                case _:
                    raise Exception(
                        gettext("Unsupported language tag: {}").format(target_lang_tag)
                    )

        case _:
            raise Exception(gettext("Unsupported language tag: {}").format(infix))

    return file_list
