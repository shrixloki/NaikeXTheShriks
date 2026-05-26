package com.example.nayki.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.Place
import androidx.compose.material.icons.filled.Share
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import com.example.nayki.ui.components.NaykiButton
import com.example.nayki.ui.components.NaykiCard
import com.example.nayki.ui.theme.Black
import com.example.nayki.ui.theme.DeepRed
import com.example.nayki.ui.theme.TextGray
import com.example.nayki.ui.theme.TextWhite
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PermissionScreen(onContinue: () -> Unit) {
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = Black
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(24.dp)
        ) {
            Text(
                text = "Safety Setup",
                color = TextWhite,
                style = MaterialTheme.typography.headlineMedium
            )
            Text(
                text = "Configure permissions to enable safety features",
                color = TextGray,
                style = MaterialTheme.typography.bodyMedium
            )

            Spacer(modifier = Modifier.height(32.dp))

            LazyColumn(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                item {
                    PermissionCard(
                        title = "Location Access",
                        description = "Used for real-time risk assessment and navigation.",
                        icon = Icons.Default.Place,
                        onEnable = {
                            scope.launch { snackbarHostState.showSnackbar("Permission flow will be connected later") }
                        }
                    )
                }
                item {
                    PermissionCard(
                        title = "Notifications",
                        description = "Receive alerts about nearby risks and SOS status.",
                        icon = Icons.Default.Notifications,
                        onEnable = {
                            scope.launch { snackbarHostState.showSnackbar("Permission flow will be connected later") }
                        }
                    )
                }
                item {
                    PermissionCard(
                        title = "Emergency Contacts",
                        description = "Quickly alert trusted contacts in case of danger.",
                        icon = Icons.Default.Share,
                        onEnable = {
                            scope.launch { snackbarHostState.showSnackbar("Contact setup will be connected later") }
                        }
                    )
                }
            }

            Spacer(modifier = Modifier.weight(1f))

            NaykiButton(
                text = "Complete Setup",
                onClick = onContinue
            )
        }
    }
}

@Composable
fun PermissionCard(
    title: String,
    description: String,
    icon: ImageVector,
    onEnable: () -> Unit
) {
    var isEnabled by remember { mutableStateOf(false) }

    NaykiCard {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = DeepRed,
                modifier = Modifier.size(32.dp)
            )
            Spacer(modifier = Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(text = title, color = TextWhite, style = MaterialTheme.typography.titleMedium)
                Text(text = description, color = TextGray, style = MaterialTheme.typography.bodySmall)
            }
            Switch(
                checked = isEnabled,
                onCheckedChange = {
                    isEnabled = it
                    if (it) onEnable()
                },
                colors = SwitchDefaults.colors(
                    checkedThumbColor = DeepRed,
                    checkedTrackColor = DeepRed.copy(alpha = 0.5f)
                )
            )
        }
    }
}
