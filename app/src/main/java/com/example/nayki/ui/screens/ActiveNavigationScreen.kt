package com.example.nayki.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Help
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Navigation
import androidx.compose.material.icons.filled.Shuffle
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.example.nayki.ui.components.NaykiCard
import com.example.nayki.ui.components.SOSButton
import com.example.nayki.ui.theme.Black
import com.example.nayki.ui.theme.DeepRed
import com.example.nayki.ui.theme.SafeGreen
import com.example.nayki.ui.theme.SurfaceDark
import com.example.nayki.ui.theme.TextGray
import com.example.nayki.ui.theme.TextWhite
import kotlinx.coroutines.launch

@Composable
fun ActiveNavigationScreen(
    onEnd: () -> Unit,
    onHelpNearby: () -> Unit,
    onSosClick: () -> Unit
) {
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()

    Box(modifier = Modifier.fillMaxSize().background(Black)) {
        // Map area with route line
        MapPlaceholder()
        
        // Instruction Card
        NaykiCard(
            modifier = Modifier
                .align(Alignment.TopCenter)
                .padding(top = 48.dp, start = 16.dp, end = 16.dp)
                .fillMaxWidth()
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.Navigation, contentDescription = null, tint = SafeGreen, modifier = Modifier.size(32.dp))
                Spacer(modifier = Modifier.width(16.dp))
                Column {
                    Text(text = "Turn left in 200m", color = TextWhite, style = MaterialTheme.typography.titleLarge)
                    Text(text = "Onto Safety Boulevard (Sample)", color = TextGray, style = MaterialTheme.typography.bodyMedium)
                }
            }
        }

        // Safety Advisory Card
        NaykiCard(
            modifier = Modifier
                .align(Alignment.Center)
                .padding(horizontal = 48.dp)
        ) {
            Text(text = "Safety Advisory: Preview", color = DeepRed, style = MaterialTheme.typography.labelMedium)
            Text(text = "Sample: Well-lit area ahead. High visibility route confidence: Preview.", color = TextWhite, style = MaterialTheme.typography.bodySmall)
        }

        // Bottom Controls
        Column(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                NaykiCard(modifier = Modifier.weight(1f)) {
                    Text(text = "12 min remaining (Sample)", color = TextWhite, style = MaterialTheme.typography.titleMedium)
                    Text(text = "3.2 km • ETA 18:42", color = TextGray, style = MaterialTheme.typography.bodySmall)
                }
                Spacer(modifier = Modifier.width(16.dp))
                SOSButton(onClick = onSosClick)
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                NavButton(
                    text = "End",
                    icon = Icons.Default.Close,
                    onClick = onEnd,
                    modifier = Modifier.weight(1f)
                )
                NavButton(
                    text = "Reroute",
                    icon = Icons.Default.Shuffle,
                    onClick = { scope.launch { snackbarHostState.showSnackbar("Calculating safer alternative...") } },
                    modifier = Modifier.weight(1f)
                )
                NavButton(
                    text = "Help",
                    icon = Icons.AutoMirrored.Filled.Help,
                    onClick = onHelpNearby,
                    modifier = Modifier.weight(1f)
                )
            }
        }

        SnackbarHost(hostState = snackbarHostState, modifier = Modifier.align(Alignment.TopCenter).padding(top = 150.dp))
    }
}

@Composable
fun NavButton(
    text: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Button(
        onClick = onClick,
        modifier = modifier.height(56.dp),
        colors = ButtonDefaults.buttonColors(containerColor = SurfaceDark),
        shape = RoundedCornerShape(12.dp),
        contentPadding = PaddingValues(0.dp)
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Icon(icon, contentDescription = null, modifier = Modifier.size(20.dp), tint = TextWhite)
            Text(text = text, style = MaterialTheme.typography.labelSmall, color = TextWhite)
        }
    }
}
