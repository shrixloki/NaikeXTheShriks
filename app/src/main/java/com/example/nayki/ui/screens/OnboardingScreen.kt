package com.example.nayki.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.nayki.ui.components.NaykiButton
import com.example.nayki.ui.theme.Black
import com.example.nayki.ui.theme.Charcoal
import com.example.nayki.ui.theme.DeepRed
import com.example.nayki.ui.theme.NaykiTheme
import com.example.nayki.ui.theme.TextGray
import com.example.nayki.ui.theme.TextWhite

@Composable
fun OnboardingScreen(onGetStarted: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Black)
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Spacer(modifier = Modifier.weight(1f))
        
        Text(
            text = "NAYKI",
            color = TextWhite,
            fontSize = 48.sp,
            fontWeight = FontWeight.Black,
            letterSpacing = 4.sp
        )
        
        Text(
            text = "Safety-first navigation",
            color = DeepRed,
            fontSize = 18.sp,
            fontWeight = FontWeight.Medium
        )
        
        Spacer(modifier = Modifier.height(48.dp))
        
        Box(
            modifier = Modifier
                .size(280.dp)
                .background(Charcoal.copy(alpha = 0.5f), MaterialTheme.shapes.large)
        ) // Placeholder for illustration
        
        Spacer(modifier = Modifier.height(48.dp))
        
        Text(
            text = "Navigate with confidence",
            color = TextWhite,
            style = MaterialTheme.typography.titleLarge,
            textAlign = TextAlign.Center
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = "Lower-risk routes, nearby help, and SOS alerts designed for your protection.",
            color = TextGray,
            textAlign = TextAlign.Center,
            modifier = Modifier.padding(horizontal = 16.dp)
        )
        
        Spacer(modifier = Modifier.weight(1f))
        
        NaykiButton(
            text = "Get Started",
            onClick = onGetStarted
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = "Your location is used only to guide and protect you",
            color = TextGray.copy(alpha = 0.5f),
            fontSize = 12.sp,
            textAlign = TextAlign.Center
        )
    }
}

@Preview(showBackground = true)
@Composable
fun OnboardingPreview() {
    NaykiTheme {
        OnboardingScreen(onGetStarted = {})
    }
}
