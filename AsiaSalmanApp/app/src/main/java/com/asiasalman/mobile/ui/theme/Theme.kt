package com.asiasalman.mobile.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.unit.LayoutDirection
import androidx.core.view.WindowCompat

private val LightColorScheme = lightColorScheme(
    primary = Primary,
    onPrimary = TextOnPrimary,
    primaryContainer = PrimaryLight,
    onPrimaryContainer = TextOnPrimary,
    secondary = Secondary,
    onSecondary = TextOnPrimary,
    secondaryContainer = Color(0xFFE5E7EB),
    onSecondaryContainer = Secondary,
    tertiary = Accent,
    onTertiary = TextOnPrimary,
    tertiaryContainer = AccentLight,
    onTertiaryContainer = PrimaryDark,
    background = Background,
    onBackground = TextPrimary,
    surface = Surface,
    onSurface = TextPrimary,
    surfaceVariant = SurfaceVariant,
    onSurfaceVariant = TextSecondary,
    error = Error,
    onError = TextOnPrimary,
    errorContainer = Color(0xFFFEE2E2),
    onErrorContainer = PrimaryDark,
    outline = CardBorder,
    outlineVariant = DividerColor,
    inverseSurface = TextPrimary,
    inverseOnSurface = Surface,
    inversePrimary = PrimaryLight
)

private val DarkColorScheme = darkColorScheme(
    primary = PrimaryLight,
    onPrimary = Surface,
    primaryContainer = PrimaryDark,
    onPrimaryContainer = AccentLight,
    secondary = Color(0xFF9CA3AF),
    onSecondary = SecondaryDark,
    secondaryContainer = Secondary,
    onSecondaryContainer = Color(0xFFE5E7EB),
    tertiary = AccentLight,
    onTertiary = PrimaryDark,
    tertiaryContainer = Accent,
    onTertiaryContainer = Surface,
    background = Color(0xFF111827),
    onBackground = Surface,
    surface = Color(0xFF1F2937),
    onSurface = Surface,
    surfaceVariant = Color(0xFF374151),
    onSurfaceVariant = Color(0xFFD1D5DB),
    error = Color(0xFFFCA5A5),
    onError = PrimaryDark,
    errorContainer = PrimaryDark,
    onErrorContainer = Color(0xFFFCA5A5),
    outline = Color(0xFF4B5563),
    outlineVariant = Color(0xFF374151),
    inverseSurface = Surface,
    inverseOnSurface = TextPrimary,
    inversePrimary = Primary
)

@Composable
fun AsiaSalmanTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme
    
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = Primary.toArgb()
            window.navigationBarColor = if (darkTheme) Color(0xFF111827).toArgb() else Surface.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = false
            WindowCompat.getInsetsController(window, view).isAppearanceLightNavigationBars = !darkTheme
        }
    }

    // Always apply RTL layout direction for Persian/Farsi
    CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Rtl) {
        MaterialTheme(
            colorScheme = colorScheme,
            typography = Typography,
            content = content
        )
    }
}
