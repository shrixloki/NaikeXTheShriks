package com.example.nayki.viewmodel

import androidx.lifecycle.ViewModel
import com.example.nayki.data.mock.SampleData
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class MapViewModel : ViewModel() {
    private val _destinations = MutableStateFlow(SampleData.destinations)
    val destinations: StateFlow<List<com.example.nayki.data.mock.Destination>> = _destinations

    private val _helpLocations = MutableStateFlow(SampleData.helpLocations)
    val helpLocations: StateFlow<List<com.example.nayki.data.mock.HelpLocation>> = _helpLocations
}
