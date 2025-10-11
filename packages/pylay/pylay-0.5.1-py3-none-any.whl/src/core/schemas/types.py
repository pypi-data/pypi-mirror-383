"""
ドメイン型定義モジュール

docs/typing-rule.md の原則1に従い、primitive型を直接使わず、
ドメイン特有の型を定義します。

3つのレベル:
- Level 1: type エイリアス（制約なし、単純な意味付け）
- Level 2: NewType + Annotated（制約付き、型レベル区別）
- Level 3: BaseModel（複雑なドメイン型・ビジネスロジック）
"""

from typing import Annotated, Literal, NewType

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, TypeAdapter

# =============================================================================
# Level 1: type エイリアス（制約なし、単純な意味付け）
# =============================================================================

type NodeId = str
"""グラフノードの一意識別子"""

type ModuleName = str
"""Pythonモジュール名"""

type VariableName = str
"""変数名"""

type TypeName = str
"""型名"""

type QualifiedName = str
"""完全修飾名（例: module.ClassName.method）"""

type FilePath = str
"""ファイルパス"""

type NodeType = Literal[
    "class",
    "function",
    "module",
    "method",
    "variable",
    "inferred_variable",
    "imported_symbol",
    "function_call",
    "method_call",
    "attribute_access",
    "type_alias",
    "unknown",
]
"""ノードタイプ"""

type InferLevel = Literal["strict", "normal", "loose", "none"]
"""型推論レベル（strict, normal, loose, none）"""


def validate_index_filename(v: str) -> str:
    """インデックスファイル名のバリデーション"""
    if not v.endswith(".md"):
        raise ValueError("インデックスファイル名は.mdで終わる必要があります")
    return v


IndexFilename = NewType("IndexFilename", str)
"""インデックスファイル名（.md拡張子必須）"""

IndexFilenameValidator: TypeAdapter[str] = TypeAdapter(
    Annotated[str, AfterValidator(validate_index_filename)]
)


def create_index_filename(value: str) -> IndexFilename:
    """インデックスファイル名を生成

    Args:
        value: ファイル名文字列

    Returns:
        検証済みのIndexFilename型

    Raises:
        ValidationError: 値が.md拡張子で終わらない場合
    """
    validated = IndexFilenameValidator.validate_python(value)
    return IndexFilename(validated)


def validate_layer_filename_template(v: str) -> str:
    """レイヤーファイル名テンプレートのバリデーション"""
    if not v.endswith(".md"):
        raise ValueError("レイヤーファイル名テンプレートは.mdで終わる必要があります")
    if "{layer}" not in v:
        raise ValueError(
            "レイヤーファイル名テンプレートには{layer}プレースホルダが必要です"
        )
    return v


LayerFilenameTemplate = NewType("LayerFilenameTemplate", str)
"""レイヤーファイル名テンプレート（.md拡張子と{layer}プレースホルダ必須）"""

LayerFilenameTemplateValidator: TypeAdapter[str] = TypeAdapter(
    Annotated[str, AfterValidator(validate_layer_filename_template)]
)


def create_layer_filename_template(value: str) -> LayerFilenameTemplate:
    """レイヤーファイル名テンプレートを生成

    Args:
        value: テンプレート文字列

    Returns:
        検証済みのLayerFilenameTemplate型

    Raises:
        ValidationError: 値が.md拡張子で終わらない、
            または{layer}プレースホルダを含まない場合
    """
    validated = LayerFilenameTemplateValidator.validate_python(value)
    return LayerFilenameTemplate(validated)


type TypeSpecName = str
"""YAML型仕様の型名"""

type TypeSpecType = str
"""YAML型仕様の基本型（str, int, float, bool, list, dict, union）"""

type Description = str
"""説明文"""

type Code = str
"""ソースコード文字列"""

type FileSuffix = str
"""ファイル拡張子（例: .py, .txt）"""

type FileOpenMode = str
"""ファイルオープンモード（w, r, a, b等）"""

type GenerateMarkdownFlag = bool
"""Markdownドキュメント生成フラグ"""

type ExtractDepsFlag = bool
"""依存関係抽出フラグ"""

type CleanOutputDirFlag = bool
"""出力ディレクトリクリーンアップフラグ"""

type Timestamp = str
"""タイムスタンプ（ISO 8601形式）"""

type Version = str
"""バージョン文字列"""

type ToolName = str
"""ツール名（mypy, ruff等）"""

type Severity = str
"""エラーや警告の重要度"""

type Message = str
"""エラーメッセージや通知メッセージ"""

type CheckCount = int
"""チェック回数や統計カウント"""

type NodeCount = int
"""ノード数"""

type EdgeCount = int
"""エッジ数"""

type Density = float
"""グラフの密度"""

type VisualizeFlag = bool
"""可視化フラグ"""

type EnableMypyFlag = bool
"""mypy統合の有効化フラグ"""

type Timeout = int
"""タイムアウト時間（秒）"""

type ClassName = str
"""クラス名"""

type FunctionName = str
"""関数名"""

type StdOut = str
"""標準出力"""

type StdErr = str
"""標準エラー出力"""

type ReturnCode = int
"""終了コード"""

type RequiredFlag = bool
"""必須フラグ（型仕様で必須かどうか）"""

type AdditionalPropertiesFlag = bool
"""追加プロパティ許可フラグ"""

type GlobPattern = str
"""Globパターン（例: **/*.py, **/tests/**）"""

type LayerName = str
"""レイヤー名（primitives, domain, api, activity等）"""

type MethodName = str
"""メソッド名（get_primitive, get_domain等）"""

type MypyFlag = str
"""mypyコマンドラインフラグ（--strict, --no-implicit-optional等）"""

type AnalyzerMode = str
"""アナライザーモード（ast, mypy, hybrid等）"""

type CyclePath = list[NodeId]
"""循環依存のパス（ノードIDのリスト）"""

type CyclePathList = list[list[NodeId]]
"""循環依存パスのリスト（各パスはノードIDのリスト）"""

type TypeRefList = list[str]
"""型参照名のリスト（例: ["User", "Post"]）"""

type TypeNameList = list[TypeName]
"""型名のリスト（TypeNameエイリアスのリスト、プリミティブ型名を表す）"""

type TypeParamList = list[str]
"""型パラメータのリスト（Generic型の引数）"""

type LayerNameList = list[LayerName]
"""レイヤー名のリスト（primitives, domain, api等）"""

type AnalyzerModeList = list[AnalyzerMode]
"""アナライザーモードのリスト"""

type MypyFlagList = list[MypyFlag]
"""mypyフラグのリスト"""

type CommandArgList = list[str]
"""コマンドライン引数のリスト"""

type CodeLineList = list[str]
"""コード行のリスト"""

type MarkdownContentList = list[str]
"""Markdownコンテンツの文字列リスト"""

type TableHeaderList = list[str]
"""Markdownテーブルのヘッダーリスト"""

type TableCellList = list[str]
"""Markdownテーブルのセルリスト"""

type TypePartList = list[str]
"""型文字列を分割したパーツのリスト"""

type ScopeStack = list[str]
"""スコープスタック（現在の処理中スコープの階層）"""

type SkipTypeSet = set[TypeName]
"""スキップする型名の集合"""

type ProcessingNodeSet = set[NodeId]
"""処理中ノード名の集合（循環参照防止用）"""

type StatisticsMap = dict[str, int]
"""統計情報のマップ（ノード数、エッジ数などのキーと整数値のペア）"""

type CheckResultData = dict[str, object]
"""チェック結果データ（汎用的なキーと値のペア）"""

type NodeAttributeValue = str | int | float | bool
"""ノード属性の値型（文字列、整数、浮動小数点、真偽値のいずれか）"""

type NodeCustomData = dict[str, NodeAttributeValue]
"""ノードカスタムデータ（ユーザーが自由に追加できる属性のマップ）"""

type CustomFields = dict[str, object]
"""カスタムフィールド（プラグインや機能拡張で追加される任意のメタデータ）"""


# =============================================================================
# Level 2: NewType + Annotated（制約付き、型レベル区別）
# =============================================================================


def validate_positive_int(v: int) -> int:
    """正の整数であることを検証するバリデーター"""
    if v <= 0:
        raise ValueError(f"正の整数である必要がありますが、{v}が指定されました")
    return v


def validate_non_negative_int(v: int) -> int:
    """非負の整数であることを検証するバリデーター"""
    if v < 0:
        raise ValueError(f"非負の整数である必要がありますが、{v}が指定されました")
    return v


# Level 2: NewType + ファクトリ関数パターン（PEP 484準拠）
PositiveInt = NewType("PositiveInt", int)
"""正の整数（> 0）"""

NonNegativeInt = NewType("NonNegativeInt", int)
"""非負の整数（>= 0）"""

# TypeAdapter（バリデーション用）
PositiveIntValidator: TypeAdapter[int] = TypeAdapter(
    Annotated[int, Field(gt=0), AfterValidator(validate_positive_int)]
)
NonNegativeIntValidator: TypeAdapter[int] = TypeAdapter(
    Annotated[int, Field(ge=0), AfterValidator(validate_non_negative_int)]
)


def create_positive_int(value: int) -> PositiveInt:
    """正の整数を生成

    Args:
        value: 整数値

    Returns:
        検証済みのPositiveInt型

    Raises:
        ValidationError: 値が正の整数でない場合
    """
    validated = PositiveIntValidator.validate_python(value)
    return PositiveInt(validated)


def create_non_negative_int(value: int) -> NonNegativeInt:
    """非負の整数を生成

    Args:
        value: 整数値

    Returns:
        検証済みのNonNegativeInt型

    Raises:
        ValidationError: 値が非負の整数でない場合
    """
    validated = NonNegativeIntValidator.validate_python(value)
    return NonNegativeInt(validated)


def validate_directory_path(v: str) -> str:
    """
    ディレクトリパスのバリデーション

    - 空文字列チェック
    - 相対パス正規化（末尾スラッシュ除去、./正規化）
    - 禁止文字チェック（null byte等）

    Note:
        存在チェックは行わない（設定時点では未作成の場合があるため）
        実際の使用時に get_absolute_paths() で絶対パス化と存在確認を行う
    """
    if not v:
        raise ValueError("ディレクトリパスは空にできません")

    # null byteチェック（セキュリティ）
    if "\0" in v:
        raise ValueError("ディレクトリパスにnull byteを含むことはできません")

    # 相対パスの正規化（末尾スラッシュ除去、冗長な./ 除去）
    normalized = v.rstrip("/")
    if normalized.startswith("./"):
        normalized = normalized[2:]

    # 空になった場合は "." にフォールバック
    if not normalized:
        normalized = "."

    return normalized


DirectoryPath = NewType("DirectoryPath", str)
"""
ディレクトリパス（相対パス）

- 空文字列不可
- 末尾スラッシュは自動削除
- 禁止文字（null byte等）をチェック
- 存在チェックは get_absolute_paths() で実施
"""

DirectoryPathValidator: TypeAdapter[str] = TypeAdapter(
    Annotated[str, AfterValidator(validate_directory_path)]
)


def create_directory_path(value: str) -> DirectoryPath:
    """ディレクトリパスを生成

    Args:
        value: ディレクトリパス文字列

    Returns:
        検証済みのDirectoryPath型

    Raises:
        ValidationError: 値が空、またはnull byteを含む場合
    """
    validated = DirectoryPathValidator.validate_python(value)
    return DirectoryPath(validated)


def validate_max_depth(v: int) -> int:
    """最大深度のバリデーション"""
    if v < 1 or v > 100:
        raise ValueError("深さは1〜100の範囲")
    return v


MaxDepth = NewType("MaxDepth", int)
"""再帰解析の最大深度（1〜100）"""

MaxDepthValidator: TypeAdapter[int] = TypeAdapter(
    Annotated[int, Field(ge=1, le=100), AfterValidator(validate_max_depth)]
)


def create_max_depth(value: int) -> MaxDepth:
    """最大深度を生成

    Args:
        value: 深度値

    Returns:
        検証済みのMaxDepth型

    Raises:
        ValidationError: 値が1〜100の範囲外の場合
    """
    validated = MaxDepthValidator.validate_python(value)
    return MaxDepth(validated)


def validate_weight(v: float) -> float:
    """重みのバリデーション"""
    if v < 0.0 or v > 1.0:
        raise ValueError("重みは0.0〜1.0の範囲")
    return v


Weight = NewType("Weight", float)
"""エッジの重み（0.0〜1.0）"""

WeightValidator: TypeAdapter[float] = TypeAdapter(
    Annotated[float, Field(ge=0.0, le=1.0), AfterValidator(validate_weight)]
)


def create_weight(value: float) -> Weight:
    """重みを生成

    Args:
        value: 重み値

    Returns:
        検証済みのWeight型

    Raises:
        ValidationError: 値が0.0〜1.0の範囲外の場合
    """
    validated = WeightValidator.validate_python(value)
    return Weight(validated)


ConfidenceScore = NewType("ConfidenceScore", float)
"""信頼度スコア（0.0〜1.0）- Weightと同じ制約"""

ConfidenceScoreValidator: TypeAdapter[float] = TypeAdapter(
    Annotated[float, Field(ge=0.0, le=1.0), AfterValidator(validate_weight)]
)


def create_confidence_score(value: float) -> ConfidenceScore:
    """信頼度スコアを生成

    Args:
        value: スコア値

    Returns:
        検証済みのConfidenceScore型

    Raises:
        ValidationError: 値が0.0〜1.0の範囲外の場合
    """
    validated = ConfidenceScoreValidator.validate_python(value)
    return ConfidenceScore(validated)


def validate_line_number(v: int) -> int:
    """行番号のバリデーション"""
    if v < 1:
        raise ValueError("行番号は1以上")
    return v


LineNumber = NewType("LineNumber", int)
"""ソースコード行番号（1以上）"""

LineNumberValidator: TypeAdapter[int] = TypeAdapter(
    Annotated[int, Field(ge=1), AfterValidator(validate_line_number)]
)


def create_line_number(value: int) -> LineNumber:
    """行番号を生成

    Args:
        value: 行番号値

    Returns:
        検証済みのLineNumber型

    Raises:
        ValidationError: 値が1未満の場合
    """
    validated = LineNumberValidator.validate_python(value)
    return LineNumber(validated)


# =============================================================================
# Level 3: BaseModel（複雑なドメイン型・ビジネスロジック）
# =============================================================================


class NodeAttributes(BaseModel):
    """
    GraphNodeの属性を表す構造化型

    primitive型の dict[str, str | int | float | bool] を
    構造化されたドメイン型に置き換えます。
    """

    model_config = ConfigDict(extra="forbid")

    # NOTE: 設計上、汎用的なカスタムデータを格納するためドメイン型エイリアスを使用
    # ユーザーが自由にキーと値を追加できるよう、NodeCustomData型を使用
    custom_data: NodeCustomData = Field(
        default_factory=dict, description="カスタム属性データ"
    )

    def get_string_value(self, key: str) -> str | None:
        """文字列値を取得"""
        value = self.custom_data.get(key)
        return str(value) if value is not None else None

    def get_int_value(self, key: str) -> int | None:
        """整数値を取得"""
        value = self.custom_data.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        return None

    def get_float_value(self, key: str) -> float | None:
        """浮動小数点値を取得"""
        value = self.custom_data.get(key)
        if isinstance(value, int | float) and not isinstance(value, bool):
            return float(value)
        return None

    def get_bool_value(self, key: str) -> bool | None:
        """真偽値を取得"""
        value = self.custom_data.get(key)
        if isinstance(value, bool):
            return value
        return None

    def has_key(self, key: str) -> bool:
        """キーが存在するか確認"""
        return key in self.custom_data

    def keys(self) -> list[str]:
        """全てのキーを取得"""
        return list(self.custom_data.keys())

    def __contains__(self, key: str) -> bool:
        """dict互換: in演算子のサポート"""
        return key in self.custom_data

    def __getitem__(self, key: str) -> str | int | float | bool:
        """dict互換: []演算子のサポート"""
        return self.custom_data[key]

    def __eq__(self, other: object) -> bool:
        """等価性チェック（dict比較にも対応）"""
        if isinstance(other, dict):
            return self.custom_data == other
        if isinstance(other, NodeAttributes):
            return self.custom_data == other.custom_data
        return False

    def __hash__(self) -> int:
        """ハッシュ値を返す"""
        return hash(tuple(sorted(self.custom_data.items())))


class GraphMetadata(BaseModel):
    """
    グラフのメタデータを表す構造化型

    primitive型の dict[str, object] を構造化されたドメイン型に置き換えます。
    """

    model_config = ConfigDict(extra="forbid")

    version: Version = Field(default="1.0", description="グラフのバージョン")
    created_at: Timestamp | None = Field(
        default=None, description="作成日時（ISO 8601形式）"
    )
    cycles: list[list[NodeId]] = Field(
        default_factory=list, description="検出された循環依存のリスト"
    )
    statistics: StatisticsMap = Field(
        default_factory=dict, description="統計情報（ノード数、エッジ数など）"
    )
    # NOTE: 設計上、拡張用のカスタムフィールドを格納するためドメイン型エイリアスを使用
    # プラグインや将来の機能拡張で任意のメタデータを追加できるよう、
    # CustomFields型を使用
    custom_fields: CustomFields = Field(
        default_factory=dict, description="カスタムフィールド"
    )

    def has_cycles(self) -> bool:
        """循環依存が存在するか確認"""
        return len(self.cycles) > 0

    def get_cycle_count(self) -> int:
        """循環依存の数を取得"""
        return len(self.cycles)

    def get_statistic(self, key: str) -> int | None:
        """統計情報を取得"""
        return self.statistics.get(key)

    def set_statistic(self, key: str, value: int) -> None:
        """統計情報を設定"""
        self.statistics[key] = value

    def get(self, key: str, default: object | None = None) -> object | None:
        """カスタムフィールドから値を取得（dict互換）"""
        return self.custom_fields.get(key, default)

    def __contains__(self, key: str) -> bool:
        """dict互換: in演算子のサポート"""
        return key in self.custom_fields

    def __getitem__(self, key: str) -> object:
        """dict互換: []演算子のサポート"""
        return self.custom_fields[key]

    def __eq__(self, other: object) -> bool:
        """等価性チェック（dict比較にも対応）"""
        if isinstance(other, dict):
            # dictとの比較時は、カスタムフィールドとして扱う
            # ただし、versionキーがある場合は特別に処理
            if "version" in other and len(other) == 1:
                return self.version == other["version"] and not self.custom_fields
            return self.custom_fields == other
        if isinstance(other, GraphMetadata):
            return (
                self.version == other.version
                and self.created_at == other.created_at
                and self.cycles == other.cycles
                and self.statistics == other.statistics
                and self.custom_fields == other.custom_fields
            )
        return False
