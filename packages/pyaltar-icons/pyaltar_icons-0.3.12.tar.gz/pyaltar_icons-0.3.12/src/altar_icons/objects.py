from aether.tags.svg import Circle, Line, Path, Rect

from ._base import BaseSVGIconElement, SVGIconAttributes

try:
    from typing import Unpack
except ImportError:
    from typing_extensions import Unpack


class EyeIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Path(
                d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"
            ),
            Circle(cx="12", cy="12", r="3"),
        ]


class EyeOffIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Path(
                d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"
            ),
            Path(d="M14.084 14.158a3 3 0 0 1-4.242-4.242"),
            Path(
                d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"
            ),
            Path(d="m2 2 20 20"),
        ]


class BanknoteIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Rect(width="20", height="12", x="2", y="6", rx="2"),
            Circle(cx="12", cy="12", r="2"),
            Path(d="M6 12h.01M18 12h.01"),
        ]


class PencilIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Path(
                d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z"
            ),
            Path(d="m15 5 4 4"),
        ]


class TrashIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Path(d="M3 6h18"),
            Path(d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"),
            Path(d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"),
        ]


class LogInIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Path(d="m10 17 5-5-5-5"),
            Path(d="M15 12H3"),
            Path(d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"),
        ]


class LogOutIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Path(d="m16 17 5-5-5-5"),
            Path(d="M21 12H9"),
            Path(d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"),
        ]


class UserIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Path(d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"),
            Circle(cx="12", cy="7", r="4"),
        ]


class UserPlusIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Path(d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"),
            Circle(cx="9", cy="7", r="4"),
            Line(x1="19", x2="19", y1="8", y2="14"),
            Line(x1="22", x2="16", y1="11", y2="11"),
        ]


class MailIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Path(d="m22 7-8.991 5.727a2 2 0 0 1-2.009 0L2 7"),
            Rect(width="20", height="16", x="2", y="4", rx="2", ry="2"),
        ]


class IdCardIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Path(d="M16 10h2"),
            Path(d="M16 14h2"),
            Path(d="M6.17 15a3 3 0 0 1 5.66 0"),
            Circle(cx="9", cy="11", r="2"),
            Rect(width="20", height="14", x="2", y="5", rx="2", ry="2"),
        ]


class LockIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Rect(width="18", height="11", x="3", y="11", rx="2", ry="2"),
            Path(d="M7 11V7a5 5 0 0 1 10 0v4"),
        ]


class LockRotateIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Rect(width="8", height="6", x="8", y="10.75", rx="1", ry="1"),
            Path(d="M10 10.25v-2a2 2 0 1 1 4 0v2"),
            Path(d="M3 12a9 9 0 1 0 9-9 9.74 9.74 0 0 0-6.74 2.74L3 8"),
            Path(d="M3 4v4h4"),
        ]


class LockQuestionMarkIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Path(d="M20 11.8V12a2 2 0 0 0-2-1H5a2 2 0 0 0-2 2v7c0 1.1.9 2 2 2h11.5"),
            Path(
                d="M18 16c.2-.4.5-.8.9-1a2.1 2.1 0 0 1 2.6.4c.3.4.5.8.5 1.3 0 1.3-2 2-2 2"
            ),
            Path(d="M20 22v.01"),
            Path(d="M7 11V7a5 5 0 0 1 10 0v4"),
        ]


class KeyRoundIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Path(
                d="M2.586 17.414A2 2 0 0 0 2 18.828V21a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h1a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h.172a2 2 0 0 0 1.414-.586l.814-.814a6.5 6.5 0 1 0-4-4z"
            ),
            Circle(fill="currentColor", cx="16.5", cy="7.5", r=".5"),
        ]


class KeyRotateIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Path(d="m14.5 9.5 1 1"),
            Path(d="m15.5 8.5-4 4"),
            Path(d="M3 12a9 9 0 1 0 9-9 9.74 9.74 0 0 0-6.74 2.74L3 8"),
            Path(d="M3 3v5h5"),
            Circle(cx="10", cy="14", r="2"),
        ]


class PanelLeftIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Rect(width="18", height="18", x="3", y="3", rx="2", ry="2"),
            Path(d="M9 3v18"),
        ]


class PanelRightIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Rect(width="18", height="18", x="3", y="3", rx="2", ry="2"),
            Path(d="M15 3v18"),
        ]


class WebsiteIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Rect(width="20", height="16", x="2", y="4", rx="2", ry="2"),
            Circle(cx="5", cy="6.5", r="0.05"),
            Circle(cx="8", cy="6.5", r="0.05"),
            Circle(cx="11", cy="6.5", r="0.05"),
            Circle(cx="12", cy="13.5", r="4.75"),
            Path(d="M12 9.5a5 5 0 0 0 0 8 5 5 0 0 0 0-8"),
            Path(d="M8 13.5h8"),
        ]


class WebsitesIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Rect(width="17", height="15", x="5", y="3", rx="2", ry="2"),
            Circle(cx="8", cy="5.5", r="0.05"),
            Circle(cx="11", cy="5.5", r="0.05"),
            Circle(cx="14", cy="5.5", r="0.05"),
            Circle(cx="13.5", cy="12", r="4"),
            Path(d="M13.5 8.5a6 5 0 0 0 0 7 6 5 0 0 0 0-7"),
            Path(d="M9.5 12h8"),
            Path(d="M2.5 8v11.5a2 2 0 0 0 2 1h14"),
        ]


class SettingsIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Path(
                d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"
            ),
            Circle(cx="12", cy="12", r="3"),
        ]


class BookOpenIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Path(d="M12 7v14"),
            Path(
                d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"
            ),
        ]


class FileIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Path(d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"),
            Path(d="M14 2v4a2 2 0 0 0 2 2h4"),
        ]


class FileTextIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Path(d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"),
            Path(d="M14 2v4a2 2 0 0 0 2 2h4"),
            Path(d="M10 9H8"),
            Path(d="M16 13H8"),
            Path(d="M16 17H8"),
        ]


class FolderIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Path(
                d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"
            )
        ]


class Share2Icon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Circle(cx="18", cy="5", r="3"),
            Circle(cx="6", cy="12", r="3"),
            Circle(cx="18", cy="19", r="3"),
            Line(x1="8.59", x2="15.42", y1="13.51", y2="17.49"),
            Line(x1="15.41", x2="8.59", y1="6.51", y2="10.49"),
        ]


class CopyIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Rect(width="14", height="14", x="8", y="8", rx="2", ry="2"),
            Path(d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"),
        ]


class SendHorizontalIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Path(
                d="M3.714 3.048a.498.498 0 0 0-.683.627l2.843 7.627a2 2 0 0 1 0 1.396l-2.842 7.627a.498.498 0 0 0 .682.627l18-8.5a.5.5 0 0 0 0-.904z"
            ),
            Path(d="M6 12h16"),
        ]


class MicIcon(BaseSVGIconElement):
    def __init__(self, **attributes: Unpack[SVGIconAttributes]):
        attributes_with_defaults = {**SVGIconAttributes.set_defaults(), **attributes}

        super().__init__(**attributes_with_defaults)

        self.children = [
            Path(d="M12 19v3"),
            Path(d="M19 10v2a7 7 0 0 1-14 0v-2"),
            Rect(width="2", height="13", x="9", y="2", rx="3", ry="3"),
        ]
