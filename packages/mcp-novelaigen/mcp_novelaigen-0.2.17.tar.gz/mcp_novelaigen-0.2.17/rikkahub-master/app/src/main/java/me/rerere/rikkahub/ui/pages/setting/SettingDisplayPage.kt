package me.rerere.rikkahub.ui.pages.setting

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.Card
import androidx.compose.material3.Icon
import androidx.compose.material3.ListItem
import androidx.compose.material3.ListItemDefaults
import androidx.compose.material3.LocalTextStyle
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Slider
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.composables.icons.lucide.Lucide
import com.composables.icons.lucide.Palette
import me.rerere.rikkahub.R
import me.rerere.rikkahub.data.datastore.DisplaySetting
import me.rerere.rikkahub.ui.components.nav.BackButton
import me.rerere.rikkahub.ui.components.richtext.MarkdownBlock
import me.rerere.rikkahub.ui.hooks.rememberAmoledDarkMode
import me.rerere.rikkahub.ui.hooks.rememberSharedPreferenceBoolean
import me.rerere.rikkahub.ui.hooks.rememberSharedPreferenceString
import me.rerere.rikkahub.ui.pages.setting.components.PresetThemeButtonGroup
import me.rerere.rikkahub.utils.plus
import org.koin.androidx.compose.koinViewModel

@Composable
fun SettingDisplayPage(vm: SettingVM = koinViewModel()) {
    val settings by vm.settings.collectAsStateWithLifecycle()
    var displaySetting by remember(settings) { mutableStateOf(settings.displaySetting) }
    var amoledDarkMode by rememberAmoledDarkMode()

    fun updateDisplaySetting(setting: DisplaySetting) {
        displaySetting = setting
        vm.updateSettings(
            settings.copy(
                displaySetting = setting
            )
        )
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(stringResource(R.string.setting_display_page_title))
                },
                navigationIcon = {
                    BackButton()
                }
            )
        }
    ) { contentPadding ->
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = contentPadding + PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            item {
                Card {
                    ListItem(
                        colors = ListItemDefaults.colors(containerColor = Color.Transparent),
                        headlineContent = {
                            Text(stringResource(R.string.setting_page_dynamic_color))
                        },
                        supportingContent = {
                            Text(stringResource(R.string.setting_page_dynamic_color_desc))
                        },
                        trailingContent = {
                            Switch(
                                checked = settings.dynamicColor,
                                onCheckedChange = {
                                    vm.updateSettings(settings.copy(dynamicColor = it))
                                },
                            )
                        },
                    )
                }
            }

            if (!settings.dynamicColor) {
                item {
                    PresetThemeButtonGroup(
                        themeId = settings.themeId,
                        type = settings.themeType,
                        modifier = Modifier.fillMaxWidth(),
                        onChangeType = {
                            vm.updateSettings(settings.copy(themeType = it))
                        },
                        onChangeTheme = {
                            vm.updateSettings(settings.copy(themeId = it))
                        }
                    )
                }
            }

            item {
                Card {
                    ListItem(
                        colors = ListItemDefaults.colors(containerColor = Color.Transparent),
                        headlineContent = {
                            Text(stringResource(R.string.setting_display_page_amoled_dark_mode_title))
                        },
                        supportingContent = {
                            Text(stringResource(R.string.setting_display_page_amoled_dark_mode_desc))
                        },
                        trailingContent = {
                            Switch(
                                checked = amoledDarkMode,
                                onCheckedChange = {
                                    amoledDarkMode = it
                                }
                            )
                        },
                    )
                }
            }

            item {
                Card {
                    ListItem(
                        colors = ListItemDefaults.colors(containerColor = Color.Transparent),
                        headlineContent = {
                            Text(stringResource(R.string.setting_display_page_show_user_avatar_title))
                        },
                        supportingContent = {
                            Text(stringResource(R.string.setting_display_page_show_user_avatar_desc))
                        },
                        trailingContent = {
                            Switch(
                                checked = displaySetting.showUserAvatar,
                                onCheckedChange = {
                                    updateDisplaySetting(displaySetting.copy(showUserAvatar = it))
                                }
                            )
                        },
                    )
                }
            }

            item {
                Card {
                    ListItem(
                        colors = ListItemDefaults.colors(containerColor = Color.Transparent),
                        headlineContent = {
                            Text(stringResource(R.string.setting_display_page_chat_list_model_icon_title))
                        },
                        supportingContent = {
                            Text(stringResource(R.string.setting_display_page_chat_list_model_icon_desc))
                        },
                        trailingContent = {
                            Switch(
                                checked = displaySetting.showModelIcon,
                                onCheckedChange = {
                                    updateDisplaySetting(displaySetting.copy(showModelIcon = it))
                                }
                            )
                        },
                    )
                }
            }

            item {
                Card {
                    ListItem(
                        colors = ListItemDefaults.colors(containerColor = Color.Transparent),
                        headlineContent = {
                            Text(stringResource(R.string.setting_display_page_show_token_usage_title))
                        },
                        supportingContent = {
                            Text(stringResource(R.string.setting_display_page_show_token_usage_desc))
                        },
                        trailingContent = {
                            Switch(
                                checked = displaySetting.showTokenUsage,
                                onCheckedChange = {
                                    updateDisplaySetting(displaySetting.copy(showTokenUsage = it))
                                }
                            )
                        },
                    )
                }
            }

            item {
                Card {
                    ListItem(
                        colors = ListItemDefaults.colors(containerColor = Color.Transparent),
                        headlineContent = {
                            Text(stringResource(R.string.setting_display_page_auto_collapse_thinking_title))
                        },
                        supportingContent = {
                            Text(stringResource(R.string.setting_display_page_auto_collapse_thinking_desc))
                        },
                        trailingContent = {
                            Switch(
                                checked = displaySetting.autoCloseThinking,
                                onCheckedChange = {
                                    updateDisplaySetting(displaySetting.copy(autoCloseThinking = it))
                                }
                            )
                        },
                    )
                }
            }

            item {
                Card {
                    ListItem(
                        colors = ListItemDefaults.colors(containerColor = Color.Transparent),
                        headlineContent = {
                            Text(stringResource(R.string.setting_display_page_show_updates_title))
                        },
                        supportingContent = {
                            Text(stringResource(R.string.setting_display_page_show_updates_desc))
                        },
                        trailingContent = {
                            Switch(
                                checked = displaySetting.showUpdates,
                                onCheckedChange = {
                                    updateDisplaySetting(displaySetting.copy(showUpdates = it))
                                }
                            )
                        },
                    )
                }
            }

            item {
                Card {
                    ListItem(
                        colors = ListItemDefaults.colors(containerColor = Color.Transparent),
                        headlineContent = {
                            Text(stringResource(R.string.setting_display_page_show_message_jumper_title))
                        },
                        supportingContent = {
                            Text(stringResource(R.string.setting_display_page_show_message_jumper_desc))
                        },
                        trailingContent = {
                            Switch(
                                checked = displaySetting.showMessageJumper,
                                onCheckedChange = {
                                    updateDisplaySetting(displaySetting.copy(showMessageJumper = it))
                                }
                            )
                        },
                    )
                }
            }

            item {
                Card {
                    ListItem(
                        colors = ListItemDefaults.colors(containerColor = Color.Transparent),
                        headlineContent = {
                            Text(stringResource(R.string.setting_display_page_enable_message_generation_haptic_effect_title))
                        },
                        supportingContent = {
                            Text(stringResource(R.string.setting_display_page_enable_message_generation_haptic_effect_desc))
                        },
                        trailingContent = {
                            Switch(
                                checked = displaySetting.enableMessageGenerationHapticEffect,
                                onCheckedChange = {
                                    updateDisplaySetting(displaySetting.copy(enableMessageGenerationHapticEffect = it))
                                }
                            )
                        },
                    )
                }
            }

            item {
                var createNewConversationOnStart by rememberSharedPreferenceBoolean(
                    "create_new_conversation_on_start",
                    true
                )
                Card {
                    ListItem(
                        colors = ListItemDefaults.colors(containerColor = Color.Transparent),
                        headlineContent = {
                            Text(stringResource(R.string.setting_display_page_create_new_conversation_on_start_title))
                        },
                        supportingContent = {
                            Text(stringResource(R.string.setting_display_page_create_new_conversation_on_start_desc))
                        },
                        trailingContent = {
                            Switch(
                                checked = createNewConversationOnStart,
                                onCheckedChange = {
                                    createNewConversationOnStart = it
                                }
                            )
                        },
                    )
                }
            }

            item {
                Card {
                    ListItem(
                        headlineContent = {
                            Text(stringResource(R.string.setting_display_page_font_size_title))
                        },
                        colors = ListItemDefaults.colors(containerColor = Color.Transparent),
                    )
                    Row(
                        modifier = Modifier
                            .padding(horizontal = 16.dp)
                            .fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Slider(
                            value = displaySetting.fontSizeRatio,
                            onValueChange = {
                                updateDisplaySetting(displaySetting.copy(fontSizeRatio = it))
                            },
                            valueRange = 0.5f..2f,
                            steps = 11,
                            modifier = Modifier.weight(1f)
                        )
                        Text(
                            text = "${(displaySetting.fontSizeRatio * 100).toInt()}%",
                        )
                    }
                    MarkdownBlock(
                        content = stringResource(R.string.setting_display_page_font_size_preview),
                        modifier = Modifier.padding(8.dp),
                        style = LocalTextStyle.current.copy(
                            fontSize = LocalTextStyle.current.fontSize * displaySetting.fontSizeRatio,
                            lineHeight = LocalTextStyle.current.lineHeight * displaySetting.fontSizeRatio,
                        )
                    )
                }
            }
        }
    }
}
