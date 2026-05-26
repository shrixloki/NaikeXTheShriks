package com.example.nayki.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.example.nayki.ui.theme.HighRiskRed
import com.example.nayki.ui.theme.ModerateOrange
import com.example.nayki.ui.theme.SafeGreen
import com.example.nayki.ui.theme.TextWhite

enum class RiskLevel {
    LOW, MODERATE, HIGH
}

@Composable
fun NaykiRiskBadge(
    level: RiskLevel,
    modifier: Modifier = Modifier
) {
    val (backgroundColor, text) = when (level) {
        RiskLevel.LOW -> SafeGreen to "Lower Risk"
        RiskLevel.MODERATE -> ModerateOrange to "Moderate Risk"
        RiskLevel.HIGH -> HighRiskRed to "Higher Risk"
    }

    Box(
        modifier = modifier
            .background(backgroundColor.copy(alpha = 0.2f), RoundedCornerShape(8.dp))
            .padding(horizontal = 8.dp, vertical = 4.dp)
    ) {
        Text(
            text = text,
            color = backgroundColor,
            style = MaterialTheme.typography.labelSmall
        )
    }
}
