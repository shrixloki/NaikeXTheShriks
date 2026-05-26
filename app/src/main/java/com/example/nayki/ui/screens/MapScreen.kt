package com.example.nayki.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.MyLocation
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.example.nayki.ui.components.NaykiSearchBar
import com.example.nayki.ui.components.SOSButton
import com.example.nayki.ui.theme.Black
import com.example.nayki.ui.theme.DeepRed
import com.example.nayki.ui.theme.NaykiTheme
import com.example.nayki.ui.theme.TextWhite
import kotlinx.coroutines.launch

@Composable
fun MapScreen(
    onSearchClick: () -> Unit,
    onSosClick: () -> Unit
) {
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()

    Box(modifier = Modifier.fillMaxSize().background(Black)) {
        // Map Placeholder: Dark grid style
        MapPlaceholder()

        // User Location Marker (center)
        Box(
            modifier = Modifier
                .size(20.dp)
                .align(Alignment.Center)
                .background(DeepRed, CircleShape)
                .border(2.dp, TextWhite, CircleShape)
        )

        // Top UI (Logo and Profile as per Image 2)
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 48.dp, start = 20.dp, end = 20.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "NAYKI",
                color = TextWhite,
                style = MaterialTheme.typography.titleLarge,
                fontWeight = androidx.compose.ui.text.font.FontWeight.Black
            )
            
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .background(DeepRed, CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Text(text = "LK", color = TextWhite, style = MaterialTheme.typography.labelLarge)
            }
        }

        // Recenter Button
        IconButton(
            onClick = {
                scope.launch { snackbarHostState.showSnackbar("Recentering map...") }
            },
            modifier = Modifier
                .align(Alignment.CenterEnd)
                .padding(end = 16.dp)
                .background(Black.copy(alpha = 0.5f), CircleShape)
        ) {
            Icon(Icons.Default.MyLocation, contentDescription = "Recenter", tint = TextWhite)
        }

        // Bottom UI (Search and SOS)
        Row(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(horizontal = 20.dp, vertical = 32.dp)
                .fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            NaykiSearchBar(
                onClick = onSearchClick,
                modifier = Modifier.weight(1f)
            )
            
            SOSButton(onClick = onSosClick)
        }

        SnackbarHost(
            hostState = snackbarHostState,
            modifier = Modifier.align(Alignment.TopCenter).padding(top = 100.dp)
        )
    }
}

@Composable
fun MapPlaceholder() {
    Box(modifier = Modifier.fillMaxSize()) {
        // Draw some grid lines to simulate a dark map
        androidx.compose.foundation.Canvas(modifier = Modifier.fillMaxSize()) {
            val strokeWidth = 1.dp.toPx()
            val color = Color(0xFF1A1A1A)
            
            // Vertical lines
            for (i in 0..10) {
                val x = size.width * i / 10f
                drawLine(color, start = androidx.compose.ui.geometry.Offset(x, 0f), end = androidx.compose.ui.geometry.Offset(x, size.height), strokeWidth = strokeWidth)
            }
            // Horizontal lines
            for (i in 0..15) {
                val y = size.height * i / 15f
                drawLine(color, start = androidx.compose.ui.geometry.Offset(0f, y), end = androidx.compose.ui.geometry.Offset(size.width, y), strokeWidth = strokeWidth)
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
fun MapPreview() {
    NaykiTheme {
        MapScreen(onSearchClick = {}, onSosClick = {})
    }
}
