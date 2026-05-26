package com.example.nayki.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.example.nayki.ui.components.NavItem
import com.example.nayki.ui.components.NaykiBottomNav
import com.example.nayki.ui.screens.*
import com.example.nayki.ui.theme.Black

object Screen {
    const val Onboarding = "onboarding"
    const val Permissions = "permissions"
    const val Map = "map"
    const val Heatmap = "heatmap"
    const val Help = "help"
    const val Profile = "profile"
    const val Search = "search"
    const val Navigation = "navigation_active"
    const val Report = "report"
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NaykiNavigation() {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    val showBottomBar = currentRoute in listOf(Screen.Map, Screen.Heatmap, Screen.Help, Screen.Profile)

    var showSosModal by remember { mutableStateOf(false) }
    var showRouteComparison by remember { mutableStateOf(false) }
    val sheetState = rememberModalBottomSheetState()

    Scaffold(
        bottomBar = {
            if (showBottomBar) {
                NaykiBottomNav(
                    currentRoute = currentRoute,
                    onNavigate = { route ->
                        navController.navigate(route) {
                            popUpTo(Screen.Map) { saveState = true }
                            launchSingleTop = true
                            restoreState = true
                        }
                    }
                )
            }
        }
    ) { padding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Onboarding,
            modifier = Modifier.padding(padding)
        ) {
            composable(Screen.Onboarding) {
                OnboardingScreen(onGetStarted = { navController.navigate(Screen.Permissions) })
            }
            composable(Screen.Permissions) {
                PermissionScreen(onContinue = { navController.navigate(Screen.Map) })
            }
            composable(Screen.Map) {
                Box {
                    MapScreen(
                        onSearchClick = { navController.navigate(Screen.Search) },
                        onSosClick = { showSosModal = true }
                    )
                    
                    if (showRouteComparison) {
                        ModalBottomSheet(
                            onDismissRequest = { showRouteComparison = false },
                            sheetState = sheetState,
                            containerColor = Black
                        ) {
                            RouteComparisonContent(
                                onStartNavigation = {
                                    showRouteComparison = false
                                    navController.navigate(Screen.Navigation)
                                },
                                onShowDetails = { /* Show details */ }
                            )
                        }
                    }
                }
            }
            composable(Screen.Heatmap) {
                HeatmapScreen()
            }
            composable(Screen.Help) {
                HelpLayerScreen()
            }
            composable(Screen.Profile) {
                ProfileScreen(onReportClick = { navController.navigate(Screen.Report) })
            }
            composable(Screen.Search) {
                DestinationSearchScreen(
                    onDestinationSelected = { _ ->
                        navController.popBackStack()
                        showRouteComparison = true
                    },
                    onBack = { navController.popBackStack() }
                )
            }
            composable(Screen.Navigation) {
                ActiveNavigationScreen(
                    onEnd = { navController.popBackStack(Screen.Map, false) },
                    onHelpNearby = { navController.navigate(Screen.Help) },
                    onSosClick = { showSosModal = true }
                )
            }
            composable(Screen.Report) {
                IncidentReportScreen(onBack = { navController.popBackStack() })
            }
        }

        if (showSosModal) {
            ModalBottomSheet(
                onDismissRequest = { showSosModal = false },
                containerColor = Black
            ) {
                SOSContent(onDismiss = { showSosModal = false })
            }
        }
    }
}
