package com.example.nayki.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.example.nayki.ui.components.NaykiCard
import com.example.nayki.ui.theme.*

@Composable
fun HeatmapScreen() {
    Box(modifier = Modifier.fillMaxSize().background(Black)) {
        // Map placeholder with "heatmap" lines
        HeatmapPlaceholder()

        Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
            // Top Bar
            Surface(
                color = Black.copy(alpha = 0.7f),
                shape = RoundedCornerShape(24.dp),
                modifier = Modifier.padding(top = 32.dp)
            ) {
                Text(
                    text = "CITY SAFETY HEATMAP",
                    color = TextWhite,
                    modifier = Modifier.padding(horizontal = 20.dp, vertical = 12.dp),
                    style = MaterialTheme.typography.labelLarge
                )
            }

            Spacer(modifier = Modifier.weight(1f))

            // Selected Area Card
            NaykiCard(modifier = Modifier.fillMaxWidth()) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(text = "Outer Ring Road", color = TextWhite, style = MaterialTheme.typography.titleLarge)
                        Text(text = "Updated 2h ago • Preview data", color = TextGray, style = MaterialTheme.typography.bodySmall)
                    }
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Badge("Poor lighting", ModerateOrange)
                        Badge("Isolated", HighRiskRed)
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Legend
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(SurfaceDark, RoundedCornerShape(12.dp))
                    .padding(12.dp),
                horizontalArrangement = Arrangement.SpaceAround
            ) {
                LegendItem("SAFE", SafeGreen)
                LegendItem("MODERATE", ModerateOrange)
                LegendItem("HIGH RISK", HighRiskRed)
            }
        }
    }
}

@Composable
fun HeatmapPlaceholder() {
    androidx.compose.foundation.Canvas(modifier = Modifier.fillMaxSize()) {
        val colors = listOf(SafeGreen, ModerateOrange, HighRiskRed)
        // Draw some blurred lines to simulate heatmap
        for (i in 0..5) {
            val startY = size.height * (0.2f + i * 0.15f)
            drawLine(
                color = colors[i % 3].copy(alpha = 0.3f),
                start = androidx.compose.ui.geometry.Offset(0f, startY),
                end = androidx.compose.ui.geometry.Offset(size.width, startY + 100f),
                strokeWidth = 40.dp.toPx()
            )
        }
    }
}

@Composable
fun LegendItem(label: String, color: Color) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Box(modifier = Modifier.size(8.dp).background(color, CircleShape))
        Spacer(modifier = Modifier.width(8.dp))
        Text(text = label, color = TextWhite, style = MaterialTheme.typography.labelSmall)
    }
}

@Composable
fun Badge(text: String, color: Color) {
    Box(
        modifier = Modifier
            .background(color.copy(alpha = 0.2f), RoundedCornerShape(12.dp))
            .padding(horizontal = 10.dp, vertical = 4.dp)
    ) {
        Text(text = text, color = color, style = MaterialTheme.typography.labelSmall)
    }
}

@Preview(showBackground = true)
@Composable
fun HeatmapPreview() {
    NaykiTheme {
        HeatmapScreen()
    }
}
