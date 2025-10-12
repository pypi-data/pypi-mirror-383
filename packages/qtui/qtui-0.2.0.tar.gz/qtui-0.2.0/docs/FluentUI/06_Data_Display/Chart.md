# Fluent UI 차트 (FluChart)

이 문서에서는 `FluentUI` 모듈에서 제공하는 차트 컴포넌트인 `FluChart`에 대해 설명합니다. 이 컴포넌트는 Qt Quick의 `Canvas` 아이템을 기반으로 하며, 강력하고 널리 사용되는 JavaScript 차트 라이브러리인 **Chart.js** (내부적으로 v2.x 버전 사용)를 활용하여 다양한 종류의 데이터를 시각화하는 기능을 제공합니다.

## 공통 임포트 방법

`FluChart` 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluChart

`FluChart`는 QML 환경에서 손쉽게 다양한 차트를 생성하고 표시할 수 있도록 설계된 컴포넌트입니다. `Canvas` 위에 그려지므로 유연한 레이아웃 구성이 가능하며, Chart.js의 풍부한 기능을 활용하여 막대, 선, 파이, 레이더 차트 등 다양한 형태의 데이터 시각화를 구현할 수 있습니다. 차트의 종류, 데이터, 그리고 세부적인 표시 옵션은 JavaScript 객체 형태의 프로퍼티를 통해 설정합니다.

### 기반 클래스

`Canvas` (from `QtQuick`)

### 주요 프로퍼티

| 이름                  | 타입         | 기본값             | 설명                                                                                                                               |
| :-------------------- | :----------- | :----------------- | :--------------------------------------------------------------------------------------------------------------------------------- |
| `chartType`           | `string`     | `undefined`        | 렌더링할 차트의 종류를 지정하는 문자열입니다. Chart.js에서 지원하는 타입 이름을 사용합니다. (예: `'bar'`, `'line'`, `'pie'`)                                |
| `chartData`           | `var`        | `undefined`        | 차트에 표시될 데이터를 정의하는 JavaScript 객체입니다. 이 객체는 Chart.js의 `data` 객체 구조를 따라야 합니다 (일반적으로 `labels`와 `datasets` 배열 포함).             |
| `chartOptions`        | `var`        | `undefined`        | 차트의 모양, 축, 범례, 툴팁, 애니메이션 등 다양한 세부 옵션을 정의하는 JavaScript 객체입니다. 이 객체는 Chart.js의 `options` 객체 구조를 따라야 합니다.                   |
| `animationDuration`   | `double`     | `300`              | 차트가 그려지거나 데이터가 업데이트될 때 애니메이션의 지속 시간(밀리초)입니다.                                                                               |
| `animationEasingType` | `enum`       | `Easing.InOutExpo` | 차트 애니메이션에 사용할 Qt Quick Easing 타입입니다.                                                                               |
| `animationRunning`    | `alias` (bool, read-only) | (내부 상태 참조)   | 현재 차트 애니메이션이 실행 중인지 여부를 나타내는 읽기 전용 프로퍼티입니다.                                                                        |

### 주요 메소드

| 이름               | 파라미터 | 반환타입 | 설명                                                                                             |
| :----------------- | :------- | :------- | :----------------------------------------------------------------------------------------------- |
| `animateToNewData` | -        | `void`   | `chartData` 프로퍼티가 변경된 후 호출해야 합니다. 변경된 데이터를 차트에 반영하고 애니메이션을 다시 시작합니다. |

### 주요 시그널

| 이름               | 파라미터 | 반환타입 | 설명                                     |
| :----------------- | :------- | :------- | :--------------------------------------- |
| `animationFinished`| -        | -        | 차트 로딩 또는 업데이트 애니메이션이 완료될 때 발생합니다. |

---

## 차트 종류 및 설정

`FluChart`의 핵심은 `chartType`, `chartData`, `chartOptions` 세 프로퍼티를 통해 Chart.js 설정을 전달하는 것입니다.

### `chartType`

생성할 차트의 종류를 문자열로 지정합니다. 자주 사용되는 타입은 다음과 같습니다:

*   `'bar'`: 세로 막대 차트
*   `'horizontalBar'`: 가로 막대 차트
*   `'line'`: 선 차트
*   `'pie'`: 파이 차트
*   `'doughnut'`: 도넛 차트
*   `'radar'`: 레이더(방사형) 차트
*   `'polarArea'`: 극지방형 차트
*   `'bubble'`: 버블 차트
*   `'scatter'`: 분산형(스캐터) 차트

(Chart.js에서 지원하는 다른 타입도 사용 가능할 수 있습니다.)

### `chartData`

차트에 표시될 데이터를 JavaScript 객체 리터럴 형식으로 제공합니다. 기본적인 구조는 다음과 같습니다:

```javascript
{
    labels: ['항목1', '항목2', '항목3'], // 각 데이터 포인트의 레이블 배열
    datasets: [ // 하나 이상의 데이터셋 배열
        {
            label: '데이터셋 제목', // 범례 등에 표시될 이름
            data: [10, 20, 30], // 실제 데이터 값 배열 (labels 배열과 크기 일치)
            backgroundColor: ['red', 'blue', 'green'], // 각 데이터 영역의 배경색
            borderColor: 'black', // 데이터 영역의 테두리 색
            borderWidth: 1 // 테두리 두께
            // ... 차트 종류에 따른 추가 데이터 속성 ...
        },
        // ... 추가 데이터셋 ...
    ]
}
```

*   `labels`: 차트의 각 데이터 포인트나 축에 해당하는 이름 배열입니다.
*   `datasets`: 하나 이상의 데이터 시리즈를 담는 배열입니다. 각 데이터셋 객체는 다음을 포함할 수 있습니다:
    *   `label`: 해당 데이터셋의 이름입니다.
    *   `data`: 실제 데이터 값의 배열입니다.
    *   `backgroundColor`, `borderColor`, `borderWidth`: 데이터 표시 요소(막대, 선, 점 등)의 색상 및 테두리 관련 속성입니다. 단일 값 또는 배열로 지정할 수 있습니다.
    *   차트 종류(`chartType`)에 따라 `fill`, `tension`, `pointBackgroundColor`, `hoverOffset`, `xAxisID`, `yAxisID` 등 다양한 추가 속성을 사용할 수 있습니다. 상세 내용은 Chart.js 문서를 참조해야 합니다.

### `chartOptions`

차트의 시각적 표현과 동작을 제어하는 다양한 옵션을 JavaScript 객체 리터럴 형식으로 제공합니다. 매우 다양한 옵션이 있으며, 주요 설정 영역은 다음과 같습니다:

```javascript
{
    responsive: true, // 부모 컨테이너 크기에 맞춰 차트 크기 자동 조절 여부
    maintainAspectRatio: false, // true일 경우 Canvas 크기에 따라 비율 유지, false 권장
    title: { // 차트 제목 설정
        display: true,
        text: '차트 제목'
    },
    legend: { // 범례 설정
        display: true,
        position: 'top' // 'top', 'bottom', 'left', 'right'
    },
    tooltips: { // 마우스 오버 시 나타나는 툴팁 설정
        enabled: true,
        mode: 'index', // 'point', 'nearest', 'index', 'dataset', 'x', 'y'
        intersect: false
    },
    scales: { // 축 설정 (막대, 선, 스캐터 차트 등)
        xAxes: [{ // X축 설정 배열
            display: true,
            stacked: false, // 축 쌓기 여부
            scaleLabel: { display: true, labelString: 'X축 이름' }
            // ... 기타 축 옵션 ...
        }],
        yAxes: [{ // Y축 설정 배열
            display: true,
            stacked: false,
            scaleLabel: { display: true, labelString: 'Y축 이름' },
            ticks: { beginAtZero: true } // 0부터 시작 여부
            // ... 기타 축 옵션 ...
        }]
    },
    // ... 차트 종류별 추가 옵션 ...
}
```

*   **`responsive`**: `true`로 설정하면 `Canvas` 크기가 변경될 때 차트 크기가 자동으로 조절됩니다.
*   **`maintainAspectRatio`**: 기본값은 `true`이며, `Canvas`의 너비와 높이 비율을 유지하려고 시도합니다. 일반적으로 QML 레이아웃과 함께 사용할 때는 `false`로 설정하여 `Canvas` 크기에 정확히 맞추는 것이 좋습니다.
*   **`title`**: 차트 상단에 표시될 제목 관련 옵션입니다.
*   **`legend`**: 데이터셋 범례의 표시 여부, 위치 등을 설정합니다.
*   **`tooltips`**: 데이터 포인트 위에 마우스를 올렸을 때 나타나는 정보 상자(툴팁)의 동작 및 모양을 설정합니다.
*   **`scales`**: 축이 있는 차트(막대, 선 등)에서 X축(`xAxes`)과 Y축(`yAxes`)의 모양, 레이블, 눈금, 쌓기(stacking) 여부 등을 설정합니다.

**참고:** `chartData`와 `chartOptions`에 대한 모든 가능한 설정은 매우 방대하므로, 원하는 커스터마이징을 위해서는 **Chart.js v2 공식 문서**를 참조하는 것이 필수적입니다.

---

## 예제

**1. 간단한 세로 막대 차트 (Bar Chart):**

```qml
import QtQuick 2.15
import FluentUI 1.0

FluFrame {
    width: 400
    height: 300
    padding: 10
    
    FluChart {
        anchors.fill: parent
        chartType: 'bar'
        chartData: {
            labels: ['월', '화', '수', '목', '금'],
            datasets: [{
                label: '방문자 수',
                data: [65, 59, 80, 81, 56],
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgb(54, 162, 235)',
                borderWidth: 1
            }]
        }
        chartOptions: {
            maintainAspectRatio: false,
            title: { display: true, text: '요일별 방문자 수' },
            legend: { display: false }, // 범례 숨김
            scales: {
                yAxes: [{ ticks: { beginAtZero: true } }]
            }
        }
    }
}
```

**2. 간단한 선 차트 (Line Chart) 및 데이터 업데이트:**

```qml
import QtQuick 2.15
import FluentUI 1.0

FluFrame {
    width: 400
    height: 300
    padding: 10

    property variant currentData: [10, 45, 23, 66, 34]

    FluChart {
        id: lineChart
        anchors.fill: parent
        chartType: 'line'
        chartData: {
            labels: ['1분기', '2분기', '3분기', '4분기', '5분기'],
            datasets: [{
                label: '매출',
                data: currentData, // property 바인딩
                fill: false, // 선 아래 영역 채우지 않음
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1 // 선 곡률 (0은 직선)
            }]
        }
        chartOptions: {
            maintainAspectRatio: false,
            title: { display: true, text: '분기별 매출' }
        }
    }
    
    FluButton {
        anchors { bottom: parent.bottom; right: parent.right; margins: 5 }
        text: "데이터 변경"
        onClicked: {
            // 데이터 변경 후 animateToNewData() 호출
            currentData = [Math.random()*100, Math.random()*100, Math.random()*100, Math.random()*100, Math.random()*100];
            lineChart.animateToNewData();
        }
    }
}
```

**3. 간단한 파이 차트 (Pie Chart):**

```qml
import QtQuick 2.15
import FluentUI 1.0

FluFrame {
    width: 300
    height: 300
    padding: 10

    FluChart {
        anchors.fill: parent
        chartType: 'pie'
        chartData: {
            labels: ['Red', 'Blue', 'Yellow'],
            datasets: [{
                label: 'Dataset 1',
                data: [300, 50, 100],
                backgroundColor: [
                    'rgb(255, 99, 132)',
                    'rgb(54, 162, 235)',
                    'rgb(255, 205, 86)'
                ],
                hoverOffset: 4 // 마우스 오버 시 조각 확장
            }]
        }
        chartOptions: {
            maintainAspectRatio: false,
            title: { display: true, text: '간단한 파이 차트' }
        }
    }
}
```

---

## 참고 사항

*   **Chart.js 의존성**: `FluChart`는 내부적으로 Chart.js 라이브러리 파일(`Chart.js`)을 사용합니다. 이 파일이 올바른 경로(`FluentUI/JS/`)에 포함되어 있어야 정상적으로 작동합니다.
*   **Chart.js 문서 참조**: `chartData`와 `chartOptions`의 복잡하고 다양한 설정을 위해서는 Chart.js (v2.x 버전 기준)의 공식 문서를 참조하는 것이 필수적입니다. QML 프로퍼티는 이 설정을 JavaScript 객체 형태로 전달하는 역할만 합니다.
*   **크기 지정**: `FluChart`는 `Canvas`이므로, 부모 아이템이나 레이아웃을 통해 명시적인 크기(width, height)를 지정해주어야 합니다. `FluFrame` 등으로 감싸는 것이 일반적입니다.
*   **동적 데이터 업데이트**: 차트 데이터를 동적으로 변경해야 할 경우, `chartData` 프로퍼티에 바인딩된 변수나 모델의 값을 변경한 후, 반드시 `FluChart` 인스턴스의 `animateToNewData()` 메소드를 호출하여 변경 사항을 차트에 반영하고 애니메이션을 트리거해야 합니다. 