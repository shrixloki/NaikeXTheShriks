package com.example.nayki.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.nayki.ui.components.NaykiButton
import com.example.nayki.ui.theme.Black
import com.example.nayki.ui.theme.DeepRed
import com.example.nayki.ui.theme.SurfaceDark
import com.example.nayki.ui.theme.TextGray
import com.example.nayki.ui.theme.TextWhite
import kotlinx.coroutines.delay

@Composable
fun SOSContent(onDismiss: () -> Unit) {
    var isTriggered by remember { mutableStateOf(false) }
    var countdown by remember { mutableStateOf(3) }

    if (isTriggered) {
        ActiveSOSState(onCancel = { isTriggered = false }, onMarkSafe = onDismiss)
    } else {
        SOSConfirmState(
            onConfirm = { isTriggered = true },
            onCancel = onDismiss
        )
    }
}

@Composable
fun SOSConfirmState(onConfirm: () -> Unit, onCancel: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "EMERGENCY ALERT",
            color = DeepRed,
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold
        )
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "Are you in immediate danger?",
            color = TextWhite,
            style = MaterialTheme.typography.titleMedium,
            textAlign = TextAlign.Center
        )
        Text(
            text = "This will notify your emergency contacts and nearby help services (Preview mode).",
            color = TextGray,
            style = MaterialTheme.typography.bodySmall,
            textAlign = TextAlign.Center,
            modifier = Modifier.padding(vertical = 16.dp)
        )

        Spacer(modifier = Modifier.height(32.dp))

        Button(
            onClick = onConfirm,
            modifier = Modifier
                .size(160.dp)
                .background(DeepRed.copy(alpha = 0.1f), CircleShape),
            colors = ButtonDefaults.buttonColors(containerColor = DeepRed),
            shape = CircleShape
        ) {
            Text(text = "TRIGGER\nALERT", textAlign = TextAlign.Center, fontWeight = FontWeight.Black)
        }

        Spacer(modifier = Modifier.height(48.dp))

        OutlinedButton(
            onClick = onCancel,
            modifier = Modifier.fillMaxWidth().height(56.dp),
            border = androidx.compose.foundation.BorderStroke(1.dp, TextGray),
            shape = RoundedCornerShape(12.dp),
            colors = ButtonDefaults.outlinedButtonColors(contentColor = TextWhite)
        ) {
            Text("Cancel")
        }
    }
}

@Composable
fun ActiveSOSState(onCancel: () -> Unit, onMarkSafe: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Box(
            modifier = Modifier
                .size(12.dp)
                .background(DeepRed, CircleShape)
        ) // Pulse indicator placeholder
        
        Text(
            text = "ALERT ACTIVE",
            color = DeepRed,
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = "Emergency alert preview active.\nBackend dispatch will connect later.",
            color = TextWhite,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(48.dp))

        NaykiButton(
            text = "Mark Safe (Sample)",
            onClick = onMarkSafe,
            containerColor = SurfaceDark
        )
        
        Spacer(modifier = Modifier.height(16.dp))

        TextButton(onClick = onCancel) {
            Text("Cancel Alert (Sample)", color = DeepRed)
        }
    }
}
