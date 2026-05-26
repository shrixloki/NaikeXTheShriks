package com.example.nayki.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.nayki.ui.theme.Black
import com.example.nayki.ui.theme.DeepRed
import com.example.nayki.ui.theme.MutedGold
import com.example.nayki.ui.theme.NaykiTheme
import com.example.nayki.ui.theme.SurfaceDark
import com.example.nayki.ui.theme.TextGray
import com.example.nayki.ui.theme.TextWhite

@Composable
fun ProfileScreen(onReportClick: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Black)
    ) {
        Spacer(modifier = Modifier.height(48.dp))

        // Profile Header
        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Box(
                modifier = Modifier
                    .size(100.dp)
                    .background(DeepRed, CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Text(text = "LK", color = TextWhite, fontSize = 40.sp, fontWeight = FontWeight.Bold)
                
                Box(
                    modifier = Modifier
                        .align(Alignment.BottomEnd)
                        .background(MutedGold, CircleShape)
                        .padding(4.dp)
                ) {
                    Icon(Icons.Default.Star, contentDescription = null, modifier = Modifier.size(16.dp), tint = Black)
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(text = "Laukik", color = TextWhite, style = MaterialTheme.typography.headlineSmall)
            Text(
                text = "GUARDIAN LEVEL MEMBER",
                color = MutedGold,
                style = MaterialTheme.typography.labelSmall,
                letterSpacing = 2.sp
            )
        }

        Spacer(modifier = Modifier.height(32.dp))

        LazyColumn(
            modifier = Modifier.fillMaxWidth(),
            contentPadding = PaddingValues(bottom = 32.dp)
        ) {
            item {
                ProfileMenuItem(
                    icon = Icons.Default.Notifications,
                    title = "Notification preferences",
                    value = "All on"
                )
            }
            item {
                ProfileMenuItem(
                    icon = Icons.Default.Navigation,
                    title = "Route defaults",
                    value = "Safest first"
                )
            }
            item {
                ProfileMenuItem(
                    icon = Icons.Default.Lock,
                    title = "Privacy settings",
                    value = "Protected"
                )
            }
            item {
                ProfileMenuItem(
                    icon = Icons.Default.Shield,
                    title = "DPDP data rights"
                )
            }
            item {
                ProfileMenuItem(
                    icon = Icons.Default.Info,
                    title = "About Nayki",
                    value = "v2.4.1"
                )
            }
            
            item {
                ProfileMenuItem(
                    icon = Icons.Default.Report,
                    title = "Report an incident",
                    onClick = onReportClick
                )
            }
            
            item {
                Spacer(modifier = Modifier.height(32.dp))
                Button(
                    onClick = { /* Logout */ },
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp)
                        .height(56.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = SurfaceDark),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text("Logout", color = DeepRed)
                }
            }
        }
        
        Spacer(modifier = Modifier.weight(1f))
        
        Text(
            text = "NAYKI • BUILT WITH CARE BY WOMEN FOR WOMEN",
            color = TextGray.copy(alpha = 0.5f),
            style = MaterialTheme.typography.labelSmall,
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            textAlign = androidx.compose.ui.text.style.TextAlign.Center
        )
    }
}

@Composable
fun ProfileMenuItem(
    icon: ImageVector,
    title: String,
    value: String? = null,
    onClick: (() -> Unit)? = null
) {
    Column(modifier = if (onClick != null) Modifier.clickable(onClick = onClick) else Modifier) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(icon, contentDescription = null, tint = TextWhite, modifier = Modifier.size(24.dp))
            Spacer(modifier = Modifier.width(16.dp))
            Text(text = title, color = TextWhite, style = MaterialTheme.typography.bodyLarge, modifier = Modifier.weight(1f))
            if (value != null) {
                Text(text = value, color = TextGray, style = MaterialTheme.typography.bodyMedium)
                Icon(Icons.Default.ChevronRight, contentDescription = null, tint = DeepRed)
            } else {
                Icon(Icons.Default.ChevronRight, contentDescription = null, tint = DeepRed)
            }
        }
        HorizontalDivider(color = SurfaceDark, thickness = 1.dp, modifier = Modifier.padding(horizontal = 16.dp))
    }
}

@Preview(showBackground = true)
@Composable
fun ProfilePreview() {
    NaykiTheme {
        ProfileScreen(onReportClick = {})
    }
}
