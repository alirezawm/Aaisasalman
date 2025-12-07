package com.asiasalman.mobile.ui.navigation

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.unit.dp
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.NavType
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.asiasalman.mobile.R
import com.asiasalman.mobile.ui.screens.about.AboutScreen
import com.asiasalman.mobile.ui.screens.auth.LoginScreen
import com.asiasalman.mobile.ui.screens.categories.CategoriesScreen
import com.asiasalman.mobile.ui.screens.contact.ContactScreen
import com.asiasalman.mobile.ui.screens.home.HomeScreen
import com.asiasalman.mobile.ui.screens.product.ProductDetailScreen
import com.asiasalman.mobile.ui.screens.search.SearchScreen
import com.asiasalman.mobile.ui.screens.splash.SplashScreen
import com.asiasalman.mobile.ui.screens.orders.OrdersScreen
import com.asiasalman.mobile.ui.screens.profile.ProfileScreen
import com.asiasalman.mobile.ui.screens.rewards.RewardsScreen
import com.asiasalman.mobile.ui.screens.shop.ShopScreen
import com.asiasalman.mobile.ui.screens.suggestions.SuggestionsScreen
import com.asiasalman.mobile.ui.theme.*

sealed class Screen(
    val route: String,
    val titleRes: Int,
    val selectedIcon: ImageVector,
    val unselectedIcon: ImageVector
) {
    object Shop : Screen(
        route = "shop",
        titleRes = R.string.nav_shop,
        selectedIcon = Icons.Rounded.Storefront,
        unselectedIcon = Icons.Outlined.Storefront
    )
    object Categories : Screen(
        route = "categories",
        titleRes = R.string.nav_categories,
        selectedIcon = Icons.Rounded.Dashboard,
        unselectedIcon = Icons.Outlined.Dashboard
    )
    object Suggestions : Screen(
        route = "suggestions",
        titleRes = R.string.nav_suggestions,
        selectedIcon = Icons.Rounded.LocalFireDepartment,
        unselectedIcon = Icons.Outlined.LocalFireDepartment
    )
    object Rewards : Screen(
        route = "rewards",
        titleRes = R.string.nav_rewards,
        selectedIcon = Icons.Rounded.CardGiftcard,
        unselectedIcon = Icons.Outlined.CardGiftcard
    )
    object Orders : Screen(
        route = "orders",
        titleRes = R.string.nav_orders,
        selectedIcon = Icons.Rounded.ShoppingBag,
        unselectedIcon = Icons.Outlined.ShoppingBag
    )
    object Profile : Screen(
        route = "profile",
        titleRes = R.string.nav_profile,
        selectedIcon = Icons.Rounded.AccountCircle,
        unselectedIcon = Icons.Outlined.AccountCircle
    )
    object Login : Screen(
        route = "login",
        titleRes = R.string.login_title,
        selectedIcon = Icons.Rounded.Login,
        unselectedIcon = Icons.Outlined.Login
    )
    object Splash : Screen(
        route = "splash",
        titleRes = R.string.app_name,
        selectedIcon = Icons.Rounded.Storefront,
        unselectedIcon = Icons.Outlined.Storefront
    )
    object ProductDetail : Screen(
        route = "product/{productId}",
        titleRes = R.string.app_name,
        selectedIcon = Icons.Rounded.ShoppingBag,
        unselectedIcon = Icons.Outlined.ShoppingBag
    ) {
        fun createRoute(productId: Int) = "product/$productId"
    }
}

val bottomNavItems = listOf(
    Screen.Shop,
    Screen.Categories,
    Screen.Suggestions,
    Screen.Rewards,
    Screen.Orders,
    Screen.Profile
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AsiaSalmanNavHost() {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination
    
    val showBottomBar = currentDestination?.route != Screen.Login.route && 
                        currentDestination?.route != Screen.Splash.route &&
                        currentDestination?.route != "contact" &&
                        currentDestination?.route != "about" &&
                        currentDestination?.route != "search" &&
                        currentDestination?.route?.startsWith("product/") != true
    
    // Ensure RTL layout direction
    CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Rtl) {
        Scaffold(
        bottomBar = {
            AnimatedVisibility(
                visible = showBottomBar,
                enter = slideInVertically(initialOffsetY = { it }),
                exit = slideOutVertically(targetOffsetY = { it })
            ) {
                NavigationBar(
                    containerColor = Surface,
                    contentColor = Primary,
                    tonalElevation = 8.dp
                ) {
                    bottomNavItems.forEach { screen ->
                        val selected = currentDestination?.hierarchy?.any { it.route == screen.route } == true
                        NavigationBarItem(
                            icon = {
                                Icon(
                                    imageVector = if (selected) screen.selectedIcon else screen.unselectedIcon,
                                    contentDescription = stringResource(screen.titleRes),
                                    modifier = Modifier.size(26.dp)
                                )
                            },
                            label = {
                                Text(
                                    text = stringResource(screen.titleRes),
                                    fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal,
                                    maxLines = 1
                                )
                            },
                            selected = selected,
                            onClick = {
                                navController.navigate(screen.route) {
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            },
                            colors = NavigationBarItemDefaults.colors(
                                selectedIconColor = Primary,
                                selectedTextColor = Primary,
                                unselectedIconColor = TextSecondary,
                                unselectedTextColor = TextSecondary,
                                indicatorColor = PrimaryLight.copy(alpha = 0.15f)
                            )
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Splash.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.Splash.route) {
                SplashScreen(navController = navController)
            }
            composable(Screen.Shop.route) {
                HomeScreen(navController = navController)
            }
            composable(Screen.Categories.route) {
                CategoriesScreen(navController = navController)
            }
            composable(Screen.Suggestions.route) {
                SuggestionsScreen(navController = navController)
            }
            composable(Screen.Rewards.route) {
                RewardsScreen(navController = navController)
            }
            composable(Screen.Orders.route) {
                OrdersScreen(navController = navController)
            }
            composable(Screen.Profile.route) {
                ProfileScreen(navController = navController)
            }
            composable(Screen.Login.route) {
                LoginScreen(navController = navController)
            }
            composable(
                route = "product/{productId}",
                arguments = listOf(
                    navArgument("productId") { type = NavType.IntType }
                )
            ) { backStackEntry ->
                val productId = backStackEntry.arguments?.getInt("productId") ?: 0
                ProductDetailScreen(
                    productId = productId,
                    navController = navController
                )
            }
            composable("contact") {
                ContactScreen(navController = navController)
            }
            composable("about") {
                AboutScreen(navController = navController)
            }
            composable("search") {
                SearchScreen(navController = navController)
            }
        }
    }
    }
}
