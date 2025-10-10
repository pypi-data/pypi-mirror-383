package me.rerere.highlight

import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.compositionLocalOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshotFlow
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.sp
import androidx.compose.ui.util.fastForEach

val LocalHighlighter = compositionLocalOf<Highlighter> { error("No Highlighter provided") }

private const val MAX_CODE_LENGTH = 4096

@Composable
fun HighlightText(
    code: String,
    language: String,
    modifier: Modifier = Modifier,
    colors: HighlightTextColorPalette = HighlightTextColorPalette.Default,
    fontSize: TextUnit = 12.sp,
    fontFamily: FontFamily = FontFamily.Monospace,
    fontStyle: FontStyle = FontStyle.Normal,
    fontWeight: FontWeight = FontWeight.Normal,
    lineHeight: TextUnit = TextUnit.Unspecified,
    overflow: TextOverflow = TextOverflow.Clip,
    softWrap: Boolean = true,
    maxLines: Int = Int.MAX_VALUE,
    minLines: Int = 1,
) {
    val highlighter = LocalHighlighter.current
    var tokens: List<HighlightToken> by remember { mutableStateOf(emptyList()) }
    var annotatedString by remember { mutableStateOf(AnnotatedString(code)) }

    val updatedCode by rememberUpdatedState(code)
    val updatedLanguage by rememberUpdatedState(language)
    LaunchedEffect(Unit) {
        snapshotFlow { updatedCode to updatedLanguage }.collect {
            tokens = if (updatedCode.length <= MAX_CODE_LENGTH) {
                highlighter.highlight(updatedCode, updatedLanguage)
            } else {
                listOf(
                    HighlightToken.Plain(content = updatedCode)
                )
            }
            annotatedString = buildAnnotatedString {
                tokens.fastForEach { token ->
                    buildHighlightText(token, colors)
                }
            }
        }
    }

    Text(
        modifier = modifier,
        text = annotatedString,
        fontSize = fontSize,
        fontFamily = fontFamily,
        fontStyle = fontStyle,
        fontWeight = fontWeight,
        lineHeight = lineHeight,
        overflow = overflow,
        softWrap = softWrap,
        maxLines = maxLines,
        minLines = minLines
    )
}

fun AnnotatedString.Builder.buildHighlightText(
    token: HighlightToken,
    colors: HighlightTextColorPalette
) {
    when (token) {
        is HighlightToken.Plain -> {
            append(token.content)
        }

        is HighlightToken.Token.StringContent -> {
            withStyle(getStyleForTokenType(token.type, colors)) {
                append(token.content)
            }
        }

        is HighlightToken.Token.StringListContent -> {
            withStyle(getStyleForTokenType(token.type, colors)) {
                token.content.fastForEach { append(it) }
            }
        }

        is HighlightToken.Token.Nested -> {
            token.content.forEach {
                buildHighlightText(it, colors)
            }
        }
    }
}

data class HighlightTextColorPalette(
    val keyword: Color,
    val string: Color,
    val number: Color,
    val comment: Color,
    val function: Color,
    val operator: Color,
    val punctuation: Color,
    val className: Color,
    val property: Color,
    val boolean: Color,
    val variable: Color,
    val tag: Color,
    val attrName: Color,
    val attrValue: Color,
    val fallback: Color
) {
    companion object {
        val Default = HighlightTextColorPalette(
            keyword = Color(0xFFCC7832),
            string = Color(0xFF6A8759),
            number = Color(0xFF6897BB),
            comment = Color(0xFF808080),
            function = Color(0xFFFFC66D),
            operator = Color(0xFFCC7832),
            punctuation = Color(0xFFCC7832),
            className = Color(0xFFCB772F),
            property = Color(0xFFCB772F),
            boolean = Color(0xFF6897BB),
            variable = Color(0xFF6A8759),
            tag = Color(0xFFE8BF6A),
            attrName = Color(0xFFBABABA),
            attrValue = Color(0xFF6A8759),
            fallback = Color(0xFF808080),
        )
    }
}

// 根据token类型返回对应的文本样式
private fun getStyleForTokenType(type: String, colors: HighlightTextColorPalette): SpanStyle {
    return when (type) {
        "keyword" -> SpanStyle(color = colors.keyword)
        "string" -> SpanStyle(color = colors.string) // 绿色
        "number" -> SpanStyle(color = colors.number) // 蓝色
        "comment" -> SpanStyle(color = colors.comment, fontStyle = FontStyle.Italic) // 灰色斜体
        "function", "method" -> SpanStyle(color = colors.function) // 黄色
        "operator" -> SpanStyle(color = colors.operator) // 橙色
        "punctuation" -> SpanStyle(color = colors.punctuation) // 橙色
        "class-name", "property" -> SpanStyle(color = colors.className) // 棕色
        "boolean", "constant" -> SpanStyle(color = colors.boolean) // 蓝色
        "regex", "important", "variable" -> SpanStyle(color = colors.variable)
        "tag" -> SpanStyle(color = colors.tag) // 黄色
        "attr-name" -> SpanStyle(color = colors.attrName) // 浅灰色
        "attr-value" -> SpanStyle(color = colors.attrValue) // 绿色
        else -> {
            // println("unknown type $type")
            SpanStyle(color = colors.fallback)
        }
    }
}
