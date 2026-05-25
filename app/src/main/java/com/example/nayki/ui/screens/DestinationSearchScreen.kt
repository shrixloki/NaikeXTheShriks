package com.example.nayki.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.History
import androidx.compose.material.icons.filled.Place
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import com.example.nayki.data.mock.SampleData
import com.example.nayki.ui.theme.Black
import com.example.nayki.ui.theme.Cream
import com.example.nayki.ui.theme.MutedGold
import com.example.nayki.ui.theme.TextGray
import com.example.nayki.ui.theme.TextWhite

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DestinationSearchScreen(
    onDestinationSelected: (String) -> Unit,
    onBack: () -> Unit
) {
    var searchQuery by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Black)
            .padding(16.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.padding(bottom = 16.dp)
        ) {
            IconButton(onClick = onBack) {
                Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = TextWhite)
            }
            TextField(
                value = searchQuery,
                onValueChange = { searchQuery = it },
                placeholder = { Text("Search destination", color = MutedGold.copy(alpha = 0.5f)) },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                colors = TextFieldDefaults.colors(
                    focusedContainerColor = Cream,
                    unfocusedContainerColor = Cream,
                    focusedTextColor = MutedGold,
                    unfocusedTextColor = MutedGold,
                    cursorColor = MutedGold,
                    focusedIndicatorColor = Color.Transparent,
                    unfocusedIndicatorColor = Color.Transparent
                ),
                shape = MaterialTheme.shapes.extraLarge
            )
        }

        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            item {
                SectionHeader("Recent Destinations")
            }
            items(SampleData.destinations) { destination ->
                SearchItem(
                    title = destination.name,
                    subtitle = destination.address,
                    icon = Icons.Default.History,
                    onClick = { onDestinationSelected(destination.name) }
                )
            }
            item {
                Spacer(modifier = Modifier.height(16.dp))
                SectionHeader("Saved Places")
            }
            item {
                SearchItem(
                    title = "Home",
                    subtitle = "123 Safety Ave",
                    icon = Icons.Default.Star,
                    onClick = { onDestinationSelected("Home") }
                )
            }
        }
    }
}

@Composable
fun SectionHeader(title: String) {
    Text(
        text = title,
        color = TextGray,
        style = MaterialTheme.typography.labelMedium,
        modifier = Modifier.padding(vertical = 8.dp)
    )
}

@Composable
fun SearchItem(
    title: String,
    subtitle: String,
    icon: ImageVector,
    onClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = TextGray,
            modifier = Modifier.size(24.dp)
        )
        Spacer(modifier = Modifier.width(16.dp))
        Column {
            Text(text = title, color = TextWhite, style = MaterialTheme.typography.titleMedium)
            Text(text = subtitle, color = TextGray, style = MaterialTheme.typography.bodySmall)
        }
    }
}
