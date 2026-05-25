package com.example.nayki.ui.components

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.vector.ImageVector
import com.example.nayki.ui.theme.Black
import com.example.nayki.ui.theme.DeepRed
import com.example.nayki.ui.theme.MutedGold
import com.example.nayki.ui.theme.TextGray

sealed class NavItem(val route: String, val title: String, val icon: ImageVector) {
    object Map : NavItem("map", "Map", Icons.Default.LocationOn)
    object Heatmap : NavItem("heatmap", "Heatmap", Icons.Default.Info)
    object Help : NavItem("help", "Help Layer", Icons.Default.Home) // Using Home as placeholder for Help
    object Profile : NavItem("profile", "Profile", Icons.Default.Person)
}

@Composable
fun NaykiBottomNav(
    currentRoute: String?,
    onNavigate: (String) -> Unit
) {
    val items = listOf(
        NavItem.Map,
        NavItem.Heatmap,
        NavItem.Help,
        NavItem.Profile
    )

    NavigationBar(
        containerColor = Black,
        contentColor = MutedGold
    ) {
        items.forEach { item ->
            NavigationBarItem(
                selected = currentRoute == item.route,
                onClick = { onNavigate(item.route) },
                icon = { Icon(item.icon, contentDescription = item.title) },
                label = { Text(item.title) },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = DeepRed,
                    selectedTextColor = DeepRed,
                    unselectedIconColor = TextGray,
                    unselectedTextColor = TextGray,
                    indicatorColor = Black
                )
            )
        }
    }
}
