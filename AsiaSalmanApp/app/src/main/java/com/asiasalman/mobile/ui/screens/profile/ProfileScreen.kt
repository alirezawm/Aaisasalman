package com.asiasalman.mobile.ui.screens.profile

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.asiasalman.mobile.ui.navigation.Screen
import com.asiasalman.mobile.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    navController: NavController,
    viewModel: ProfileViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Background)
    ) {
        // Gradient Header
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    Brush.verticalGradient(
                        colors = listOf(Primary, PrimaryDark)
                    )
                )
        ) {
            Column(
                modifier = Modifier.fillMaxWidth()
            ) {
                TopAppBar(
                    title = {
                        Text(
                            text = "پروفایل",
                            fontWeight = FontWeight.Bold
                        )
                    },
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = Color.Transparent,
                        titleContentColor = Color.White
                    )
                )
                
                // Profile Header
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    // Avatar with shadow
                    Box(
                        modifier = Modifier
                            .size(100.dp)
                            .shadow(8.dp, CircleShape)
                            .clip(CircleShape)
                            .background(Color.White),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            Icons.Rounded.Person,
                            contentDescription = null,
                            modifier = Modifier.size(60.dp),
                            tint = Primary
                        )
                    }
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    if (uiState.isLoggedIn && uiState.user != null) {
                        Text(
                            text = uiState.user!!.fullName ?: "کاربر",
                            style = MaterialTheme.typography.titleLarge,
                            color = Color.White,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = uiState.user!!.phone,
                            style = MaterialTheme.typography.bodyMedium,
                            color = Color.White.copy(alpha = 0.9f)
                        )
                        
                        if (uiState.user!!.isBulkBuyer) {
                            Spacer(modifier = Modifier.height(10.dp))
                            Surface(
                                color = Accent,
                                shape = RoundedCornerShape(20.dp)
                            ) {
                                Row(
                                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 6.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(
                                        Icons.Rounded.Verified,
                                        contentDescription = null,
                                        modifier = Modifier.size(16.dp),
                                        tint = Color.White
                                    )
                                    Spacer(modifier = Modifier.width(6.dp))
                                    Text(
                                        text = "خریدار عمده",
                                        style = MaterialTheme.typography.labelMedium,
                                        color = Color.White,
                                        fontWeight = FontWeight.Medium
                                    )
                                }
                            }
                        }
                    } else {
                        Text(
                            text = "مهمان",
                            style = MaterialTheme.typography.titleLarge,
                            color = Color.White,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(12.dp))
                        Button(
                            onClick = { navController.navigate(Screen.Login.route) },
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color.White,
                                contentColor = Primary
                            ),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Icon(
                                Icons.Rounded.Login,
                                contentDescription = null,
                                modifier = Modifier.size(18.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                "ورود / ثبت نام",
                                fontWeight = FontWeight.Medium
                            )
                        }
                    }
                }
            }
        }
        
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
        ) {
            Spacer(modifier = Modifier.height(16.dp))
            
            // Menu Items
            ProfileMenuCard {
                ProfileMenuItem(
                    icon = Icons.Rounded.Edit,
                    title = "ویرایش پروفایل",
                    onClick = { /* Navigate to edit profile */ }
                )
                
                Divider(color = DividerColor, modifier = Modifier.padding(horizontal = 16.dp))
                
                ProfileMenuItem(
                    icon = Icons.Rounded.BusinessCenter,
                    title = "درخواست خریدار عمده",
                    subtitle = if (uiState.user?.isBulkBuyer == true) "✓ فعال" else "غیرفعال",
                    onClick = { /* Navigate to bulk buyer request */ }
                )
                
                Divider(color = DividerColor, modifier = Modifier.padding(horizontal = 16.dp))
                
                ProfileMenuItem(
                    icon = Icons.Rounded.Receipt,
                    title = "تاریخچه سفارشات",
                    onClick = { navController.navigate(Screen.Orders.route) }
                )
                
                Divider(color = DividerColor, modifier = Modifier.padding(horizontal = 16.dp))
                
                ProfileMenuItem(
                    icon = Icons.Rounded.FavoriteBorder,
                    title = "علاقه‌مندی‌ها",
                    onClick = { /* Navigate to wishlist */ }
                )
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            ProfileMenuCard {
                ProfileMenuItem(
                    icon = Icons.Rounded.Notifications,
                    title = "تنظیمات اعلان‌ها",
                    onClick = { /* Navigate to notification settings */ }
                )
                
                Divider(color = DividerColor, modifier = Modifier.padding(horizontal = 16.dp))
                
                ProfileMenuItemWithSwitch(
                    icon = Icons.Rounded.Palette,
                    title = "تم برنامه",
                    checked = uiState.isDarkMode,
                    onCheckedChange = { viewModel.toggleDarkMode() }
                )
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            ProfileMenuCard {
                ProfileMenuItem(
                    icon = Icons.Rounded.Info,
                    title = "درباره ما",
                    onClick = { navController.navigate("about") }
                )
                
                Divider(color = DividerColor, modifier = Modifier.padding(horizontal = 16.dp))
                
                ProfileMenuItem(
                    icon = Icons.Rounded.SupportAgent,
                    title = "تماس با ما",
                    onClick = { navController.navigate("contact") }
                )
            }
            
            if (uiState.isLoggedIn) {
                Spacer(modifier = Modifier.height(12.dp))
                
                ProfileMenuCard {
                    ProfileMenuItem(
                        icon = Icons.Rounded.Logout,
                        title = "خروج از حساب",
                        iconTint = Error,
                        titleColor = Error,
                        onClick = { viewModel.logout() }
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // App Version
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    Icons.Rounded.Verified,
                    contentDescription = null,
                    modifier = Modifier.size(16.dp),
                    tint = TextSecondary
                )
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = "نسخه 1.0.0",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary
                )
            }
            
            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}

@Composable
fun ProfileMenuCard(
    content: @Composable ColumnScope.() -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Surface),
        elevation = CardDefaults.cardElevation(2.dp)
    ) {
        Column(content = content)
    }
}

@Composable
fun ProfileMenuItem(
    icon: ImageVector,
    title: String,
    subtitle: String? = null,
    iconTint: Color = Primary,
    titleColor: Color = TextPrimary,
    onClick: () -> Unit
) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        color = Color.Transparent
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .background(iconTint.copy(alpha = 0.1f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = iconTint,
                    modifier = Modifier.size(22.dp)
                )
            }
            
            Spacer(modifier = Modifier.width(14.dp))
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.bodyLarge,
                    color = titleColor,
                    fontWeight = FontWeight.Medium
                )
                subtitle?.let {
                    Text(
                        text = it,
                        style = MaterialTheme.typography.bodySmall,
                        color = if (it.contains("✓")) Success else TextSecondary
                    )
                }
            }
            
            Icon(
                Icons.Rounded.ChevronRight,
                contentDescription = null,
                tint = TextSecondary,
                modifier = Modifier.size(24.dp)
            )
        }
    }
}

@Composable
fun ProfileMenuItemWithSwitch(
    icon: ImageVector,
    title: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit,
    iconTint: Color = Primary
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = Color.Transparent
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .background(iconTint.copy(alpha = 0.1f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = iconTint,
                    modifier = Modifier.size(22.dp)
                )
            }
            
            Spacer(modifier = Modifier.width(14.dp))
            
            Text(
                text = title,
                style = MaterialTheme.typography.bodyLarge,
                color = TextPrimary,
                fontWeight = FontWeight.Medium,
                modifier = Modifier.weight(1f)
            )
            
            Switch(
                checked = checked,
                onCheckedChange = onCheckedChange,
                colors = SwitchDefaults.colors(
                    checkedThumbColor = Color.White,
                    checkedTrackColor = Primary,
                    uncheckedThumbColor = Color.White,
                    uncheckedTrackColor = TextSecondary.copy(alpha = 0.5f)
                )
            )
        }
    }
}
