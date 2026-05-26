package com.example.nayki.data.mock

import com.example.nayki.ui.components.RiskLevel

data class Destination(val name: String, val address: String)
data class RouteOption(
    val type: String,
    val eta: String,
    val distance: String,
    val riskLevel: RiskLevel,
    val safetyScore: String,
    val riskReason: String,
    val timeDiff: String? = null
)
data class HelpLocation(
    val name: String,
    val type: String,
    val distance: String,
    val isOpen: Boolean
)

object SampleData {
    val destinations = listOf(
        Destination("Home", "123 Safety Ave"),
        Destination("Work", "456 Guard St"),
        Destination("Central Mall", "789 Plaza Rd"),
        Destination("City Hospital", "101 Care Blvd")
    )

    val routes = listOf(
        RouteOption("Fastest Route", "15 min", "4.2 km", RiskLevel.MODERATE, "Safety: 72", "High traffic area", null),
        RouteOption("Lower-Risk Route", "18 min", "4.8 km", RiskLevel.LOW, "Safety: 94", "Well-lit main roads", "+3 min"),
        RouteOption("Balanced Route", "16 min", "4.5 km", RiskLevel.LOW, "Safety: 85", "Standard route", "+1 min")
    )

    val helpLocations = listOf(
        HelpLocation("City Police Station", "Police", "0.5 km", true),
        HelpLocation("General Hospital", "Hospital", "1.2 km", true),
        HelpLocation("24/7 Pharmacy", "Pharmacy", "0.8 km", true),
        HelpLocation("Safe Haven Cafe", "Public Place", "0.3 km", true)
    )
}
