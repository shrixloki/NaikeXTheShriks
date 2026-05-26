package com.example.nayki.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Call
import androidx.compose.material.icons.filled.Navigation
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.example.nayki.data.mock.SampleData
import com.example.nayki.ui.components.NaykiCard
import com.example.nayki.ui.theme.Black
import com.example.nayki.ui.theme.DeepRed
import com.example.nayki.ui.theme.SafeGreen
import com.example.nayki.ui.theme.SurfaceDark
import com.example.nayki.ui.theme.TextGray
import com.example.nayki.ui.theme.TextWhite
import kotlinx.coroutines.launch

@Composable
fun HelpLayerScreen() {
    val filters = listOf("All", "Police", "Hospital", "Pharmacy", "Public Place")
    var selectedFilter by remember { mutableStateOf("All") }
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = Black
    ) { padding ->
        Box(modifier = Modifier.fillMaxSize().padding(padding)) {
            // Map background placeholder
            MapPlaceholder()

            Column(modifier = Modifier.fillMaxSize()) {
                LazyRow(
                    modifier = Modifier.padding(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(filters) { filter ->
                        FilterChip(
                            selected = selectedFilter == filter,
                            onClick = { selectedFilter = filter },
                            label = { Text(filter) },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = DeepRed,
                                selectedLabelColor = TextWhite,
                                containerColor = SurfaceDark.copy(alpha = 0.5f),
                                labelColor = TextWhite
                            )
                        )
                    }
                }

                Spacer(modifier = Modifier.weight(1f))

                LazyColumn(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(300.dp)
                        .padding(horizontal = 16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    items(SampleData.helpLocations.filter { selectedFilter == "All" || it.type == selectedFilter }) { help ->
                        HelpLocationCard(
                            name = help.name,
                            type = help.type,
                            distance = help.distance,
                            isOpen = help.isOpen,
                            onCall = { scope.launch { snackbarHostState.showSnackbar("Calling ${help.name} (Preview UI only)...") } },
                            onNavigate = { scope.launch { snackbarHostState.showSnackbar("Navigating to ${help.name} (Sample)...") } }
                        )
                    }
                }
                Spacer(modifier = Modifier.height(16.dp))
            }
        }
    }
}

@Composable
fun HelpLocationCard(
    name: String,
    type: String,
    distance: String,
    isOpen: Boolean,
    onCall: () -> Unit,
    onNavigate: () -> Unit
) {
    NaykiCard {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(text = name, color = TextWhite, style = MaterialTheme.typography.titleMedium)
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(text = "$type • $distance", color = TextGray, style = MaterialTheme.typography.bodySmall)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = if (isOpen) "Open" else "Closed",
                        color = if (isOpen) SafeGreen else DeepRed,
                        style = MaterialTheme.typography.labelSmall
                    )
                }
            }
            
            Row {
                IconButton(onClick = onCall) {
                    Icon(Icons.Default.Call, contentDescription = "Call", tint = DeepRed)
                }
                IconButton(onClick = onNavigate) {
                    Icon(Icons.Default.Navigation, contentDescription = "Navigate", tint = SafeGreen)
                }
            }
        }
    }
}
