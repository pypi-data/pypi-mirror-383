# Fluent UI 애플리케이션 설정 (FluApp)

이 문서에서는 `FluentUI` 모듈의 `FluApp` 전역 싱글톤 객체에 대해 설명합니다. `FluApp`은 Fluent UI 애플리케이션의 전역적인 설정과 초기화, 그리고 일부 유틸리티 기능을 담당합니다.

## `FluApp` 접근 방법

`FluApp`은 QML 환경과 Python 환경 양쪽에서 접근할 수 있는 싱글톤 객체입니다.

**QML:**

QML에서는 전역 싱글톤으로 등록되어 있으므로, 별도의 import 없이 `FluApp` 식별자를 사용하여 직접 접근할 수 있습니다.

```qml
import FluentUI 1.0

FluWindow {
    // FluApp의 설정을 참조하거나 변경 (변경은 권장되지 않음)
    title: FluApp.useSystemAppBar ? "System AppBar" : "Custom AppBar"
    icon: FluApp.windowIcon 
}

// 초기화는 보통 Python에서 수행
Component.onCompleted: {
    // FluApp.init(this) // QML에서 직접 init 호출은 일반적이지 않음
}
```

**Python:**

Python 코드에서는 `FluApp` 클래스를 임포트하고 `getInstance()` 메소드를 통해 싱글톤 인스턴스를 얻어 사용합니다. **애플리케이션 초기화 시 Python에서 `init()` 메소드를 호출하는 것이 필수적입니다.**

```python
import sys
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QLocale

# FluentUI 플러그인 경로 설정 (필요시)
# addImportPath("../src/qtui") 

from qtui.FluentUI import FluApp # FluApp 임포트

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    app.setWindowIcon(QIcon("app_icon.ico"))
    
    engine = QQmlApplicationEngine()
    engine.load("main.qml") 
    
    if not engine.rootObjects():
        sys.exit(-1)
        
    # FluApp 초기화 (필수)
    flu_app = FluApp.getInstance()
    flu_app.init(engine.rootObjects()[0]) # 메인 QML 객체 전달
    # flu_app.init(engine.rootObjects()[0], QLocale(QLocale.English)) # 특정 로케일 지정
    
    # 전역 설정 예시 (init 호출 전에 설정해도 됨)
    flu_app.useSystemAppBar = False # 커스텀 앱 바 사용 (기본값)
    flu_app.windowIcon = "qrc:/res/default_icon.ico" # 기본 창 아이콘 설정
    
    sys.exit(app.exec())
```

---

## FluApp

`FluApp` 싱글톤 객체는 Fluent UI 애플리케이션의 전역 동작 방식에 영향을 미치는 핵심 설정들을 관리합니다. 개발자는 애플리케이션 시작 시 이 객체의 `init()` 메소드를 호출하여 로케일 및 번역 설정을 초기화하고, 필요에 따라 `useSystemAppBar`, `windowIcon` 등의 프로퍼티를 설정하여 앱 전체의 기본 창 스타일과 아이콘 등을 지정할 수 있습니다.

### 기반 클래스

`QObject` (싱글톤)

### 주요 프로퍼티

| 이름             | 타입     | 기본값  | 설명                                                                                                                                |
| :--------------- | :------- | :------ | :---------------------------------------------------------------------------------------------------------------------------------- |
| `useSystemAppBar`| `bool`   | `false` | `true`로 설정하면 모든 `FluWindow`가 시스템 기본 창 테두리와 제목 표시줄을 사용합니다. `false`이면 `FluWindow`는 프레임리스 모드로 작동하고 사용자 정의 `FluAppBar`를 사용합니다. | 
| `windowIcon`     | `string` | `None`  | 애플리케이션의 모든 `FluWindow`에 기본적으로 적용될 창 아이콘의 URL(경로)입니다. `None`이거나 설정되지 않으면 창에 아이콘이 표시되지 않거나 OS 기본값이 사용될 수 있습니다.        |
| `locale`         | `QLocale`| `None`  | 애플리케이션의 현재 로케일입니다. `init()` 메소드 호출 시 설정되며, `qsTr` 등을 통한 국제화 처리에 사용됩니다.                                                     |
| `launcher`       | `QObject`| `None`  | `init()` 메소드에서 전달받은, 애플리케이션을 시작한 주 QML 객체(보통 메인 윈도우 또는 `ApplicationWindow`)에 대한 참조입니다.                                          |

### 주요 메소드

| 이름       | 파라미터                                                | 반환타입     | 설명                                                                                                                                                                                                      |
| :--------- | :------------------------------------------------------ | :----------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `init`     | `launcher: QObject`, `locale: QLocale = QLocale.system()` | `void`       | `FluApp` 객체를 초기화합니다. **애플리케이션 시작 시 반드시 한 번 호출해야 합니다.** `launcher`는 메인 QML 객체를, `locale`은 사용할 로케일(기본값: 시스템 로케일)을 지정합니다. 내부적으로 번역 파일 로드 등을 수행합니다. | 
| `iconData` | `keyword: string = ""`                                  | `list[dict]` | `FluentIcons`에 정의된 아이콘 데이터를 검색하여 `{name: string, icon: int}` 형태의 딕셔너리 리스트를 반환합니다. `keyword`가 포함된 아이콘 이름만 필터링합니다. 아이콘 선택기 등에 활용될 수 있습니다.                   |

### 주요 시그널

프로퍼티 값이 변경될 때 해당 시그널이 발생합니다.

*   `useSystemAppBarChanged()`
*   `windowIconChanged()`
*   `localeChanged()`
*   `launcherChanged()`

### 예제

(위의 Python 접근 방법 섹션의 예제 코드를 참조하십시오. `init()` 호출, `useSystemAppBar`, `windowIcon` 설정 방법을 보여줍니다.)

**QML에서 아이콘 데이터 사용 예시:**

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import FluentUI 1.0

ListView {
    model: FluApp.iconData("Arrow") // "Arrow" 키워드가 포함된 아이콘 검색
    delegate: Row {
        spacing: 5
        FluIcon { iconSource: modelData.icon } // 아이콘 표시
        FluText { text: modelData.name }       // 아이콘 이름 표시
    }
}
```

### 관련 컴포넌트/객체

*   **`FluWindow`**: `FluApp`의 설정(`useSystemAppBar`, `windowIcon`)에 따라 동작이나 외관이 변경됩니다.
*   **`FluTheme`**: 테마 관련 전역 설정을 담당합니다. `FluApp`과 함께 사용되어 앱의 전체적인 룩앤필을 결정합니다.
*   **`FluRouter`**: 창 탐색을 관리하며, `FluApp`에서 `routes` 설정을 관리할 수 있습니다.
*   **`FluentIcons`**: `iconData()` 메소드를 통해 아이콘 정보를 제공합니다.

### 참고 사항

*   **`init()` 호출 필수**: `FluApp`의 기능을 제대로 사용하려면 애플리케이션 시작 시 Python 코드에서 `FluApp.getInstance().init(...)`를 반드시 호출해야 합니다. 이는 특히 로케일 설정 및 번역 기능에 중요합니다.
*   **싱글톤**: `FluApp`은 싱글톤 패턴으로 구현되어 애플리케이션 전체에서 단 하나의 인스턴스만 존재합니다.
*   **전역 설정의 영향**: `useSystemAppBar`와 같은 설정은 애플리케이션의 모든 `FluWindow`에 영향을 미치므로, 일반적으로 애플리케이션 시작 시 한 번 설정하고 동적으로 변경하지 않는 것이 좋습니다. 