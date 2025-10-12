# Import local modules
from qtui.dayu.theme import MTheme
from qtui.dayu.types import HeaderData, ModelData


def score_color(score: float, _: ModelData):
    if score < 60:
        return MTheme().error_color
    elif score < 80:
        return MTheme().warning_color
    elif score >= 90:
        return MTheme().success_color
    return MTheme().info_color


def font_underline(x: float, _: ModelData):
    return {"underline": True}


def font_bold(x: float, _: ModelData):
    return {"bold": True}


def sex_icon_color(x: str, _: ModelData):
    return (f"{x.lower()}.svg", "skyblue" if x == "Male" else "pink")


def age_display(x: float, _: ModelData):
    return f"{x} years old"


def city_display(x: list[str] | str, _: ModelData):
    if isinstance(x, list):
        return " & ".join(x)
    return x


def city_bg_color(x: str, _: ModelData):
    if x:
        return "transparent"
    return MTheme().error_color


header_list: list[HeaderData] = [
    {
        "label": "Name",
        "key": "name",
        "checkable": True,
        "searchable": True,
        "width": 200,
        "font": font_underline,
        "icon": "user_fill.svg",
    },
    {
        "label": "Sex",
        "key": "sex",
        "searchable": True,
        "selectable": True,
        "icon": sex_icon_color,
    },
    {
        "label": "Age",
        "key": "age",
        "width": 90,
        "searchable": True,
        "editable": True,
        "display": age_display,
        "font": font_bold,
    },
    {
        "label": "Address",
        "key": "city",
        "selectable": True,
        "searchable": True,
        "exclusive": False,
        "width": 120,
        "display": city_display,
        "bg_color": city_bg_color,
    },
    {
        "label": "Score",
        "key": "score",
        "searchable": True,
        "editable": True,
        "order": "desc",
        "bg_color": score_color,
        "color": "#fff",
    },
    {"label": "Score Copy", "key": "score", "searchable": True, "color": score_color},
]

data_list: list[ModelData] = [
    {
        "name": "John Brown",
        "sex": "Male",
        "sex_list": ["Male", "Female"],
        "age": 18,
        "score": 89,
        "city": "New York",
        "city_list": ["New York", "Ottawa", "London", "Sydney"],
        "date": "2016-10-03",
    },
    {
        "name": "Jim Green",
        "sex": "Male",
        "sex_list": ["Male", "Female"],
        "age": 24,
        "score": 55,
        "city": "London",
        "city_list": ["New York", "Ottawa", "London", "Sydney"],
        "date": "2016-10-01",
    },
    {
        "name": "Zhang Xiaoming",
        "sex": "Male",
        "sex_list": ["Male", "Female"],
        "age": 30,
        "score": 70,
        "city": "",
        "city_list": ["Beijing", "Shanghai", "Shenzhen", "Guangzhou"],
        "date": "2016-10-02",
    },
    {
        "name": "Jon Snow",
        "sex": "Female",
        "sex_list": ["Male", "Female"],
        "age": 26,
        "score": 60,
        "city": "Ottawa",
        "city_list": ["New York", "Ottawa", "London", "Sydney"],
        "date": "2016-10-04",
    },
    {
        "name": "Li Xiaohua",
        "sex": "Female",
        "sex_list": ["Male", "Female"],
        "age": 18,
        "score": 97,
        "city": "Ottawa",
        "city_list": ["New York", "Ottawa", "London", "Sydney"],
        "date": "2016-10-04",
    },
]

tree_data_list: list[ModelData] = [
    {
        "name": "John Brown",
        "sex": "Male",
        "sex_list": ["Male", "Female"],
        "age": 18,
        "score": 89,
        "city": "New York",
        "city_list": ["New York", "Ottawa", "London", "Sydney"],
        "date": "2016-10-03",
        "children": [
            {
                "name": "Jim Green",
                "sex": "Male",
                "sex_list": ["Male", "Female"],
                "age": 24,
                "score": 55,
                "city": "London",
                "city_list": ["New York", "Ottawa", "London", "Sydney"],
                "date": "2016-10-01",
            },
            {
                "name": "Zhang Xiaoming",
                "sex": "Male",
                "sex_list": ["Male", "Female"],
                "age": 30,
                "score": 70,
                "city": "",
                "city_list": ["Beijing", "Shanghai", "Shenzhen", "Guangzhou"],
                "date": "2016-10-02",
            },
        ],
    },
    {
        "name": "Jon Snow",
        "sex": "Female",
        "sex_list": ["Male", "Female"],
        "age": 26,
        "score": 60,
        "city": "Ottawa",
        "city_list": ["New York", "Ottawa", "London", "Sydney"],
        "date": "2016-10-04",
    },
    {
        "name": "Li Xiaohua",
        "sex": "Female",
        "sex_list": ["Male", "Female"],
        "age": 18,
        "score": 97,
        "city": "Ottawa",
        "city_list": ["New York", "Ottawa", "London", "Sydney"],
        "date": "2016-10-04",
    },
]
