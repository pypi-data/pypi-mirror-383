# Fluent UI 원격 로더 (FluRemoteLoader)

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluRemoteLoader` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 원격 URL 또는 로컬 파일 시스템으로부터 QML 콘텐츠를 비동기적으로 로드하고 표시하는 기능을 제공하며, 로딩 과정을 시각적으로 나타내는 상태 관리 기능을 포함합니다.

`FluRemoteLoader`는 내부적으로 Qt Quick의 `Loader`를 사용하며, 이를 `FluStatusLayout`으로 감싸 로딩 중, 성공, 오류 상태를 사용자에게 명확하게 보여줍니다.

## 공통 임포트 방법

`FluRemoteLoader` 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluRemoteLoader

`FluRemoteLoader`는 외부 QML 파일을 동적으로 로드해야 하는 시나리오를 간편하게 처리하기 위해 설계되었습니다. 웹 상의 QML 파일, 로컬 파일 시스템의 QML 파일, 또는 Qt 리소스 시스템 내의 QML 파일을 `source` 프로퍼티에 지정하여 로드할 수 있습니다. 로딩이 진행되는 동안에는 로딩 표시기를 보여주고, 로딩이 성공하면 해당 QML 콘텐츠를 표시하며, 오류 발생 시에는 오류 메시지와 함께 재시도 옵션을 제공합니다. 또한, 캐시 문제없이 콘텐츠를 강제로 새로고침하는 `reload()` 메소드를 제공하여 핫 리로딩(Hot Reloading)과 같은 개발 편의 기능을 구현하는 데 유용합니다.

### 기반 클래스

`FluStatusLayout` (from `FluentUI`)

`FluRemoteLoader`는 `FluStatusLayout`을 상속하므로, `FluStatusLayout`의 모든 프로퍼티, 메소드, 시그널을 사용할 수 있습니다. 예를 들어, 로딩, 성공, 오류 상태에 표시될 아이템(`loadingItem`, `successItem`, `errorItem`), 상태 모드(`statusMode`), 오류 메시지(`errorText`), 오류 상태 클릭 시그널(`onErrorClicked`) 등을 활용하거나 재정의할 수 있습니다.

### 고유/특징적 프로퍼티

| 이름     | 타입     | 기본값    | 설명                                                                                                                                                           |
| :------- | :------- | :-------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `source` | `url`    | `""`      | 로드할 QML 콘텐츠의 URL 또는 로컬 파일 경로입니다. URL 스킴(예: `http`, `https`, `file`, `qrc`)을 포함해야 합니다. 이 값이 변경되면 자동으로 로딩을 시도합니다 (단, `lazy`가 `false`일 경우). |
| `lazy`   | `bool`   | `false`   | 지연 로딩 활성화 여부입니다. `true`로 설정하면 컴포넌트가 생성될 때 `source` 값이 있어도 바로 로딩하지 않고, 이후 `source` 프로퍼티가 명시적으로 설정되거나 변경될 때 로딩을 시작합니다.           |

### 고유 메소드

| 이름           | 파라미터 | 반환타입      | 설명                                                                                                                                                            |
| :------------- | :------- | :------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `reload()`     | -        | `void`        | 현재 `source`에 지정된 QML 콘텐츠를 강제로 다시 로드합니다. 내부적으로 URL에 타임스탬프(`?` + `Date.now()`)를 추가하여 QML 엔진 및 네트워크 캐시를 우회하려고 시도합니다. 로딩 실패 시 재시도 또는 핫 리로딩 구현에 사용됩니다. |
| `itemLodaer()` | -        | `FluLoader` | 내부에 사용된 `FluLoader` 인스턴스를 반환합니다. 로딩 상태나 로드된 아이템에 직접 접근해야 하는 고급 시나리오에서 사용할 수 있습니다.                                                              |

### 고유 시그널

`FluRemoteLoader` 자체에 정의된 고유 시그널은 없습니다. 하지만 `FluStatusLayout`으로부터 상속받은 `onErrorClicked` 시그널을 사용할 수 있습니다. 이 시그널은 오류 상태 화면에서 사용자가 재시도 영역을 클릭했을 때 발생하며, `FluRemoteLoader`에서는 이 시그널이 발생하면 내부적으로 `reload()` 메소드가 호출되도록 연결되어 있습니다.

---

## 예제

**1. 원격 QML 로드 (기본 사용법)**

다음은 웹 상의 QML 파일을 로드하는 가장 기본적인 예제입니다 (`T_RemoteLoader.qml` 기반).

```qml
import QtQuick 2.15
import FluentUI 1.0

FluPage {
    // ... 페이지 설정 ...

    FluRemoteLoader {
        anchors.fill: parent
        // 웹 상의 QML 파일 URL을 source로 지정
        source: "https://zhuzichu.gitee.io/Qt_174_RemoteLoader.qml" 
    }
}
```
이 코드는 `FluPage`가 표시될 때 지정된 URL로부터 QML 파일을 비동기적으로 로드합니다. 로딩 중에는 `FluStatusLayout`의 기본 로딩 표시기가, 로딩이 완료되면 해당 QML 콘텐츠가, 오류 발생 시에는 오류 메시지와 재시도 버튼이 표시됩니다.

**2. 로컬 QML 핫 리로딩 (고급 사용법)**

다음은 로컬 QML 파일을 드래그 앤 드롭으로 로드하고, 해당 파일이 변경될 때마다 자동으로 리로드하는 '핫 리로딩' 기능을 구현한 예제입니다 (`HotloadWindow.qml` 기반).

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import FluentUI 1.0
import Qt.labs.platform 1.1 // FileDialog, FileWatcher 등 사용 시 필요

FluWindow {
    id: window
    width: 800; height: 600
    title: "QML Hot Loader"

    // 파일 변경 감지기
    FileWatcher {
        id: fileWatcher
        // 파일 경로 목록 (여기서는 하나만 감시)
        // path 프로퍼티는 FileWatcher에 실제로는 없으므로, files 리스트 사용 필요
        // files: ["file:///path/to/watch.qml"] 
        property url currentPath: ""
        files: currentPath ? [FluTools.urlToLocalFile(currentPath)] : []
        onFileChanged: (path) => {
            console.log("File changed:", path)
            remoteLoader.reload() // 파일 변경 시 reload() 호출
        }
    }

    FluFrame {
        anchors.fill: parent

        FluRemoteLoader {
            id: remoteLoader
            anchors.fill: parent
            lazy: true // Drop 이벤트 발생 시 source를 설정하므로 lazy 로딩 사용
            
            // 사용자 정의 오류 아이템: 로딩 실패 시 상세 오류 메시지 표시
            errorItem: Item {
                anchors.fill: parent
                FluText {
                    text: remoteLoader.itemLodaer().status === Loader.Error ? 
                          remoteLoader.itemLodaer().sourceComponent.errorString() : "Unknown Error"
                    color: "red"
                    wrapMode: Text.WrapAnywhere
                    anchors.centerIn: parent
                    padding: 20
                }
                // 기본 재시도 기능 사용 (FluStatusLayout의 errorItem 역할)
                MouseArea{
                    anchors.fill: parent
                    onClicked: remoteLoader.onErrorClicked()
                }
            }
        }

        // 파일이 로드되지 않았을 때 안내 메시지
        FluText {
            text: qsTr("Drag a QML file here")
            font: FluTextStyle.Title
            anchors.centerIn: parent
            visible: !remoteLoader.itemLodaer().item && remoteLoader.statusMode === FluStatusLayoutType.Success
        }

        // 드래그 중일 때 시각적 피드백
        Rectangle {
            anchors.fill: parent
            color: "#33333333"
            visible: dropArea.containsDrag
            radius: 5
        }

        // 드롭 영역 설정
        DropArea {
            id: dropArea
            anchors.fill: parent
            onEntered: (event) => {
                // QML 파일만 허용하도록 필터링
                if (event.hasUrls && event.urls[0].toString().endsWith(".qml")) {
                    event.acceptProposedAction()
                } else {
                    event.accepted = false
                }
            }
            onDropped: (event) => {
                var fileUrl = event.urls[0]
                console.log("File dropped:", fileUrl.toString())
                remoteLoader.source = fileUrl // source 설정하여 로딩 시작
                fileWatcher.currentPath = fileUrl // FileWatcher가 감시할 경로 업데이트
                // 파일 변경 감지를 위해 files 리스트 업데이트 필요
                // fileWatcher.files = [FluTools.urlToLocalFile(fileUrl)] 
            }
        }
    }
}
```
이 예제에서는 `DropArea`를 사용하여 QML 파일을 창으로 드래그하면 해당 파일의 URL을 `FluRemoteLoader`의 `source`로 설정합니다. 동시에 `FileWatcher`가 해당 파일의 변경을 감지하도록 설정하고, 파일이 변경되면 `remoteLoader.reload()`를 호출하여 화면을 자동으로 업데이트합니다. 또한, 로딩 실패 시 상세 오류 메시지를 보여주기 위해 `errorItem`을 커스터마이징했습니다.

---

## 참고 사항

*   **비동기 로딩 및 상태 표시**: `FluRemoteLoader`는 네트워크 또는 파일 시스템으로부터 콘텐츠를 비동기적으로 로드합니다. 이 과정 동안 사용자는 `FluStatusLayout`이 제공하는 로딩 상태(기본 로딩 애니메이션), 성공 상태(로드된 QML 콘텐츠), 또는 오류 상태(오류 메시지 및 재시도 옵션)를 보게 됩니다. `loadingItem`, `errorItem` 등을 통해 이 상태 표시를 커스터마이징할 수 있습니다.
*   **캐싱과 `reload()`**: 웹 서버 응답 헤더나 QML 엔진 자체의 메커니즘으로 인해 원격 또는 로컬 리소스가 캐싱될 수 있습니다. `reload()` 메소드는 URL에 타임스탬프 쿼리 파라미터를 추가하여 이러한 캐시를 우회하고 항상 서버나 파일 시스템에서 최신 콘텐츠를 가져오려고 시도합니다. 이는 특히 개발 중 핫 리로딩 시나리오에서 유용합니다. 하지만 모든 종류의 캐싱을 완벽하게 우회한다고 보장할 수는 없습니다.
*   **오류 처리**: QML 파일을 로드하는 과정(네트워크 통신, 파일 접근, QML 파싱 등)에서 오류가 발생하면 `FluRemoteLoader`는 자동으로 오류 상태로 전환됩니다. 기본 오류 화면에는 재시도 기능이 포함되어 있으며, 사용자가 이를 클릭하면 `onErrorClicked` 시그널이 발생하고 내부적으로 `reload()`가 호출됩니다. 더 자세한 오류 원인을 사용자에게 보여주고 싶다면, `errorItem`을 사용자 정의 컴포넌트로 지정하고 해당 컴포넌트 내에서 `remoteLoader.itemLodaer().sourceComponent.errorString()` (주의: `itemLodaer().status`가 `Loader.Error`일 때만 유효) 등을 통해 오류 메시지에 접근하여 표시할 수 있습니다.
*   **로컬 파일 경로**: 로컬 파일 시스템의 QML 파일을 로드할 때는 `file:///` 스킴으로 시작하는 절대 경로를 사용해야 합니다. Qt의 리소스 시스템(`qrc:/`) 내에 포함된 QML 파일도 `source`로 지정하여 로드할 수 있습니다. 