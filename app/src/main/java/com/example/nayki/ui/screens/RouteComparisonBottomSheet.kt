package com.example.nayki.ui.screens

import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.example.nayki.data.mock.RouteOption
import com.example.nayki.data.mock.SampleData
import com.example.nayki.ui.components.NaykiButton
import com.example.nayki.ui.components.NaykiRiskBadge
import com.example.nayki.ui.theme.DeepRed
import com.example.nayki.ui.theme.SafeGreen
import com.example.nayki.ui.theme.SurfaceDark
import com.example.nayki.ui.theme.TextGray
import com.example.nayki.ui.theme.TextWhite

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RouteComparisonContent(
    onStartNavigation: (RouteOption) -> Unit,
    onShowDetails: (RouteOption) -> Unit
) {
    var selectedRoute by remember { mutableStateOf(SampleData.routes[1]) } // Default to Lower-Risk

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
    ) {
        Text(
            text = "Compare Routes",
            color = TextWhite,
            style = MaterialTheme.typography.titleLarge
        )
        Text(
            text = "Safety confidence: Preview",
            color = TextGray,
            style = MaterialTheme.typography.labelSmall
        )

        Spacer(modifier = Modifier.height(16.dp))

        LazyColumn(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            items(SampleData.routes) { route ->
                RouteOptionCard(
                    route = route,
                    isSelected = route == selectedRoute,
                    onSelect = { selectedRoute = route }
                )
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            OutlinedButton(
                onClick = { onShowDetails(selectedRoute) },
                modifier = Modifier.weight(1f).height(56.dp),
                shape = RoundedCornerShape(12.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, TextGray),
                colors = ButtonDefaults.outlinedButtonColors(contentColor = TextWhite)
            ) {
                Text("Details")
            }
            NaykiButton(
                text = "Start",
                onClick = { onStartNavigation(selectedRoute) },
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
fun RouteOptionCard(
    route: RouteOption,
    isSelected: Boolean,
    onSelect: () -> Unit
) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onSelect)
            .border(
                width = if (isSelected) 2.dp else 1.dp,
                color = if (isSelected) DeepRed else SurfaceDark,
                shape = RoundedCornerShape(16.dp)
            ),
        shape = RoundedCornerShape(16.dp),
        color = SurfaceDark
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(text = route.type, color = TextWhite, style = MaterialTheme.typography.titleMedium)
                    Text(text = "${route.eta} • ${route.distance}", color = TextGray, style = MaterialTheme.typography.bodySmall)
                }
                NaykiRiskBadge(level = route.riskLevel)
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = route.safetyScore,
                    color = DeepRed,
                    style = MaterialTheme.typography.labelLarge
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "• Sample risk reason: ${route.riskReason}",
                    color = TextGray,
                    style = MaterialTheme.typography.bodySmall
                )
            }
            
            route.timeDiff?.let {
                Text(
                    text = it,
                    color = if (it.startsWith("+")) TextGray else SafeGreen,
                    style = MaterialTheme.typography.labelSmall
                )
            }
        }
    }
}
