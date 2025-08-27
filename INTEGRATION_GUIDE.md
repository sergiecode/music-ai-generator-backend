# 🎵 Music AI Generator Backend - Integration Guide

**Created by Sergie Code - Software Engineer & Programming Educator**

This guide provides comprehensive instructions for integrating with the Music AI Generator Backend API. Use this documentation to build frontend applications (Angular, React, Vue.js) and mobile applications (Flutter, React Native) that connect to the backend service.

---

## 📋 **Table of Contents**

1. [API Overview](#api-overview)
2. [Authentication & Security](#authentication--security)
3. [Core API Endpoints](#core-api-endpoints)
4. [Integration Patterns](#integration-patterns)
5. [Frontend Integration (Angular 20)](#frontend-integration-angular-20)
6. [Mobile Integration (Flutter)](#mobile-integration-flutter)
7. [Error Handling](#error-handling)
8. [Real-time Features](#real-time-features)
9. [Performance Optimization](#performance-optimization)
10. [Testing Integration](#testing-integration)

---

## 🌐 **API Overview**

### **Base Configuration**
```javascript
const API_CONFIG = {
  baseURL: 'http://127.0.0.1:8000',  // Development
  // baseURL: 'https://your-production-domain.com',  // Production
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
};
```

### **Key Features**
- ✅ **RESTful API** with JSON responses
- ✅ **CORS Enabled** for frontend integration
- ✅ **Async Processing** with status tracking
- ✅ **Input Validation** with detailed error messages
- ✅ **Interactive Documentation** at `/docs`
- ✅ **Health Monitoring** endpoints

---

## 🔐 **Authentication & Security**

### **Current Implementation**
The backend currently **does not require authentication** for development purposes. All endpoints are publicly accessible.

### **Production Recommendations**
For production deployment, implement:

```javascript
// Future JWT Authentication Pattern
const authHeaders = {
  'Authorization': `Bearer ${userToken}`,
  'X-API-Key': 'your-api-key'
};
```

### **Rate Limiting**
- **Development**: No rate limiting
- **Production**: Implement rate limiting (e.g., 100 requests/hour per user)

### **Security Best Practices**
```javascript
// Input Sanitization Example
function sanitizePrompt(prompt) {
  return prompt
    .trim()
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .substring(0, 500); // Max length validation
}
```

---

## 🚀 **Core API Endpoints**

### **1. Health Check**
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "music-ai-generator-backend"
}
```

**Usage Example:**
```javascript
async function checkServerHealth() {
  try {
    const response = await fetch(`${API_CONFIG.baseURL}/health`);
    const data = await response.json();
    return data.status === 'healthy';
  } catch (error) {
    console.error('Server health check failed:', error);
    return false;
  }
}
```

### **2. Service Information**
```http
GET /music/
```

**Response:**
```json
{
  "service": "Music AI Generator",
  "version": "1.0.0",
  "supported_formats": ["mp3", "wav"],
  "max_duration": 300,
  "min_duration": 5,
  "status": "active"
}
```

### **3. Generate Music** ⭐
```http
POST /music/generate
```

**Request Body:**
```json
{
  "prompt": "relaxing piano melody for meditation",
  "duration": 60
}
```

**Validation Rules:**
- `prompt`: Required, 1-500 characters, non-empty after trimming
- `duration`: Optional, integer between 5-300 seconds (default: 30)

**Response:**
```json
{
  "success": true,
  "message": "Music generation started for prompt: 'relaxing piano melody for meditation'",
  "track_id": "track_a1b2c3d4",
  "prompt": "relaxing piano melody for meditation",
  "duration": 60,
  "estimated_processing_time": 45,
  "status": "processing",
  "download_url": null
}
```

**Error Responses:**
```json
// Validation Error (422)
{
  "detail": [
    {
      "loc": ["body", "prompt"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}

// Business Logic Error (400)
{
  "detail": "Prompt cannot be empty"
}
```

### **4. Track Status** ⭐
```http
GET /music/status/{track_id}
```

**Response:**
```json
{
  "track_id": "track_a1b2c3d4",
  "status": "processing", // "processing" | "completed" | "failed"
  "progress": 75,         // 0-100
  "prompt": "relaxing piano melody for meditation",
  "duration": 60,
  "created_at": "2025-08-27T10:30:00Z",
  "estimated_completion": "2025-08-27T10:31:00Z",
  "download_url": null    // Available when status is "completed"
}
```

**Status Values:**
- `processing`: Generation in progress
- `completed`: Ready for download
- `failed`: Generation failed

---

## 🔄 **Integration Patterns**

### **1. Basic Music Generation Flow**

```javascript
class MusicGeneratorClient {
  constructor(baseURL = 'http://127.0.0.1:8000') {
    this.baseURL = baseURL;
  }

  async generateMusic(prompt, duration = 30) {
    try {
      const response = await fetch(`${this.baseURL}/music/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt.trim(),
          duration: duration
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Generation failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Music generation error:', error);
      throw error;
    }
  }

  async getTrackStatus(trackId) {
    try {
      const response = await fetch(`${this.baseURL}/music/status/${trackId}`);
      
      if (!response.ok) {
        throw new Error('Track not found');
      }

      return await response.json();
    } catch (error) {
      console.error('Status check error:', error);
      throw error;
    }
  }

  async pollTrackStatus(trackId, onProgress = null) {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const status = await this.getTrackStatus(trackId);
          
          if (onProgress) {
            onProgress(status);
          }

          if (status.status === 'completed') {
            resolve(status);
          } else if (status.status === 'failed') {
            reject(new Error('Generation failed'));
          } else {
            setTimeout(poll, 2000); // Poll every 2 seconds
          }
        } catch (error) {
          reject(error);
        }
      };
      
      poll();
    });
  }
}
```

### **2. Complete Usage Example**

```javascript
async function generateAndWaitForMusic() {
  const client = new MusicGeneratorClient();
  
  try {
    // 1. Generate music
    const generation = await client.generateMusic(
      "upbeat electronic dance music",
      90
    );
    
    console.log(`Generation started: ${generation.track_id}`);
    
    // 2. Poll for completion with progress updates
    const completedTrack = await client.pollTrackStatus(
      generation.track_id,
      (status) => {
        console.log(`Progress: ${status.progress}%`);
        updateProgressBar(status.progress);
      }
    );
    
    // 3. Handle completion
    console.log('Generation completed!');
    console.log(`Download URL: ${completedTrack.download_url}`);
    
    return completedTrack;
    
  } catch (error) {
    console.error('Generation failed:', error);
    showErrorMessage(error.message);
  }
}
```

---

## 🅰️ **Frontend Integration (Angular 20)**

### **Service Implementation**

```typescript
// music-generator.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, Subject, interval } from 'rxjs';
import { switchMap, takeWhile, catchError } from 'rxjs/operators';

export interface MusicGenerationRequest {
  prompt: string;
  duration?: number;
}

export interface MusicGenerationResponse {
  success: boolean;
  message: string;
  track_id: string;
  prompt: string;
  duration: number;
  estimated_processing_time: number;
  status: string;
  download_url: string | null;
}

export interface TrackStatus {
  track_id: string;
  status: 'processing' | 'completed' | 'failed';
  progress: number;
  prompt: string;
  duration: number;
  created_at: string;
  estimated_completion: string;
  download_url: string | null;
}

@Injectable({
  providedIn: 'root'
})
export class MusicGeneratorService {
  private readonly baseURL = 'http://127.0.0.1:8000';
  private progressSubject = new Subject<TrackStatus>();

  constructor(private http: HttpClient) {}

  generateMusic(request: MusicGenerationRequest): Observable<MusicGenerationResponse> {
    return this.http.post<MusicGenerationResponse>(
      `${this.baseURL}/music/generate`,
      request
    ).pipe(
      catchError(this.handleError)
    );
  }

  getTrackStatus(trackId: string): Observable<TrackStatus> {
    return this.http.get<TrackStatus>(
      `${this.baseURL}/music/status/${trackId}`
    ).pipe(
      catchError(this.handleError)
    );
  }

  pollTrackStatus(trackId: string): Observable<TrackStatus> {
    return interval(2000).pipe(
      switchMap(() => this.getTrackStatus(trackId)),
      takeWhile(status => status.status === 'processing', true),
      catchError(this.handleError)
    );
  }

  getProgressUpdates(): Observable<TrackStatus> {
    return this.progressSubject.asObservable();
  }

  checkServerHealth(): Observable<{ status: string; service: string }> {
    return this.http.get<{ status: string; service: string }>(
      `${this.baseURL}/health`
    );
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An unknown error occurred';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Server-side error
      if (error.status === 422) {
        errorMessage = 'Invalid input parameters';
      } else if (error.status === 400) {
        errorMessage = error.error.detail || 'Bad request';
      } else if (error.status === 404) {
        errorMessage = 'Track not found';
      } else {
        errorMessage = `Server error: ${error.status}`;
      }
    }
    
    throw new Error(errorMessage);
  }
}
```

### **Component Implementation**

```typescript
// music-generator.component.ts
import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Subscription } from 'rxjs';
import { MusicGeneratorService, TrackStatus } from './music-generator.service';

@Component({
  selector: 'app-music-generator',
  templateUrl: './music-generator.component.html',
  styleUrls: ['./music-generator.component.scss']
})
export class MusicGeneratorComponent implements OnInit, OnDestroy {
  musicForm: FormGroup;
  isGenerating = false;
  currentTrack: TrackStatus | null = null;
  error: string | null = null;
  
  private subscription = new Subscription();

  constructor(
    private fb: FormBuilder,
    private musicService: MusicGeneratorService
  ) {
    this.musicForm = this.fb.group({
      prompt: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(500)]],
      duration: [30, [Validators.required, Validators.min(5), Validators.max(300)]]
    });
  }

  ngOnInit() {
    this.checkServerConnection();
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

  async checkServerConnection() {
    try {
      await this.musicService.checkServerHealth().toPromise();
      console.log('Server connection established');
    } catch (error) {
      this.error = 'Cannot connect to server. Please ensure the backend is running.';
    }
  }

  onSubmit() {
    if (this.musicForm.valid && !this.isGenerating) {
      this.generateMusic();
    }
  }

  private generateMusic() {
    this.isGenerating = true;
    this.error = null;
    this.currentTrack = null;

    const request = this.musicForm.value;

    this.subscription.add(
      this.musicService.generateMusic(request).subscribe({
        next: (response) => {
          console.log('Generation started:', response);
          this.startPolling(response.track_id);
        },
        error: (error) => {
          this.error = error.message;
          this.isGenerating = false;
        }
      })
    );
  }

  private startPolling(trackId: string) {
    this.subscription.add(
      this.musicService.pollTrackStatus(trackId).subscribe({
        next: (status) => {
          this.currentTrack = status;
          
          if (status.status === 'completed') {
            this.isGenerating = false;
            console.log('Generation completed!', status);
          } else if (status.status === 'failed') {
            this.error = 'Music generation failed';
            this.isGenerating = false;
          }
        },
        error: (error) => {
          this.error = error.message;
          this.isGenerating = false;
        }
      })
    );
  }

  downloadTrack() {
    if (this.currentTrack?.download_url) {
      window.open(this.currentTrack.download_url, '_blank');
    }
  }

  reset() {
    this.currentTrack = null;
    this.error = null;
    this.isGenerating = false;
    this.musicForm.reset({ duration: 30 });
  }
}
```

### **Template Implementation**

```html
<!-- music-generator.component.html -->
<div class="music-generator-container">
  <h1>🎵 Music AI Generator</h1>
  <p class="subtitle">Created by Sergie Code</p>

  <!-- Error Display -->
  <div *ngIf="error" class="alert alert-danger">
    {{ error }}
  </div>

  <!-- Generation Form -->
  <form [formGroup]="musicForm" (ngSubmit)="onSubmit()" class="generation-form">
    <div class="form-group">
      <label for="prompt">Music Description</label>
      <textarea
        id="prompt"
        formControlName="prompt"
        placeholder="Describe the music you want to generate (e.g., 'relaxing piano melody')"
        class="form-control"
        rows="3"
        [class.is-invalid]="musicForm.get('prompt')?.invalid && musicForm.get('prompt')?.touched"
      ></textarea>
      <div *ngIf="musicForm.get('prompt')?.invalid && musicForm.get('prompt')?.touched" class="invalid-feedback">
        Please enter a valid music description (1-500 characters).
      </div>
    </div>

    <div class="form-group">
      <label for="duration">Duration (seconds)</label>
      <input
        type="number"
        id="duration"
        formControlName="duration"
        min="5"
        max="300"
        class="form-control"
        [class.is-invalid]="musicForm.get('duration')?.invalid && musicForm.get('duration')?.touched"
      >
      <small class="form-text text-muted">Between 5 and 300 seconds</small>
      <div *ngIf="musicForm.get('duration')?.invalid && musicForm.get('duration')?.touched" class="invalid-feedback">
        Duration must be between 5 and 300 seconds.
      </div>
    </div>

    <button
      type="submit"
      class="btn btn-primary btn-lg"
      [disabled]="musicForm.invalid || isGenerating"
    >
      <span *ngIf="isGenerating" class="spinner-border spinner-border-sm" role="status"></span>
      {{ isGenerating ? 'Generating...' : 'Generate Music' }}
    </button>
  </form>

  <!-- Progress Display -->
  <div *ngIf="currentTrack" class="progress-container">
    <h3>Generation Progress</h3>
    <div class="track-info">
      <p><strong>Track ID:</strong> {{ currentTrack.track_id }}</p>
      <p><strong>Prompt:</strong> {{ currentTrack.prompt }}</p>
      <p><strong>Duration:</strong> {{ currentTrack.duration }} seconds</p>
      <p><strong>Status:</strong> {{ currentTrack.status }}</p>
    </div>

    <div class="progress mb-3">
      <div
        class="progress-bar"
        [style.width.%]="currentTrack.progress"
        [class.bg-success]="currentTrack.status === 'completed'"
        [class.bg-danger]="currentTrack.status === 'failed'"
      >
        {{ currentTrack.progress }}%
      </div>
    </div>

    <!-- Download Button -->
    <button
      *ngIf="currentTrack.status === 'completed' && currentTrack.download_url"
      class="btn btn-success"
      (click)="downloadTrack()"
    >
      📥 Download Track
    </button>

    <!-- Reset Button -->
    <button
      *ngIf="currentTrack.status === 'completed' || currentTrack.status === 'failed'"
      class="btn btn-secondary ml-2"
      (click)="reset()"
    >
      🔄 Generate Another
    </button>
  </div>
</div>
```

### **Styling (SCSS)**

```scss
// music-generator.component.scss
.music-generator-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  
  h1 {
    text-align: center;
    color: #2c3e50;
    margin-bottom: 0.5rem;
  }
  
  .subtitle {
    text-align: center;
    color: #7f8c8d;
    margin-bottom: 2rem;
  }
}

.generation-form {
  background: #f8f9fa;
  padding: 2rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  
  .form-group {
    margin-bottom: 1.5rem;
  }
  
  label {
    font-weight: 600;
    color: #2c3e50;
  }
  
  .btn-primary {
    background-color: #3498db;
    border-color: #3498db;
    width: 100%;
  }
}

.progress-container {
  background: #ffffff;
  padding: 2rem;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  
  h3 {
    color: #2c3e50;
    margin-bottom: 1rem;
  }
  
  .track-info {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
    
    p {
      margin-bottom: 0.5rem;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
  }
  
  .progress {
    height: 20px;
  }
}

.alert {
  border-radius: 4px;
  margin-bottom: 1rem;
}

.spinner-border-sm {
  margin-right: 0.5rem;
}
```

---

## 📱 **Mobile Integration (Flutter)**

### **API Service Implementation**

```dart
// lib/services/music_generator_service.dart
import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;

class MusicGenerationRequest {
  final String prompt;
  final int? duration;

  MusicGenerationRequest({required this.prompt, this.duration});

  Map<String, dynamic> toJson() => {
    'prompt': prompt,
    if (duration != null) 'duration': duration,
  };
}

class MusicGenerationResponse {
  final bool success;
  final String message;
  final String trackId;
  final String prompt;
  final int duration;
  final int estimatedProcessingTime;
  final String status;
  final String? downloadUrl;

  MusicGenerationResponse({
    required this.success,
    required this.message,
    required this.trackId,
    required this.prompt,
    required this.duration,
    required this.estimatedProcessingTime,
    required this.status,
    this.downloadUrl,
  });

  factory MusicGenerationResponse.fromJson(Map<String, dynamic> json) {
    return MusicGenerationResponse(
      success: json['success'],
      message: json['message'],
      trackId: json['track_id'],
      prompt: json['prompt'],
      duration: json['duration'],
      estimatedProcessingTime: json['estimated_processing_time'],
      status: json['status'],
      downloadUrl: json['download_url'],
    );
  }
}

class TrackStatus {
  final String trackId;
  final String status;
  final int progress;
  final String prompt;
  final int duration;
  final String createdAt;
  final String estimatedCompletion;
  final String? downloadUrl;

  TrackStatus({
    required this.trackId,
    required this.status,
    required this.progress,
    required this.prompt,
    required this.duration,
    required this.createdAt,
    required this.estimatedCompletion,
    this.downloadUrl,
  });

  factory TrackStatus.fromJson(Map<String, dynamic> json) {
    return TrackStatus(
      trackId: json['track_id'],
      status: json['status'],
      progress: json['progress'],
      prompt: json['prompt'],
      duration: json['duration'],
      createdAt: json['created_at'],
      estimatedCompletion: json['estimated_completion'],
      downloadUrl: json['download_url'],
    );
  }
}

class MusicGeneratorService {
  static const String baseUrl = 'http://10.0.2.2:8000'; // Android emulator
  // static const String baseUrl = 'http://127.0.0.1:8000'; // iOS simulator
  // static const String baseUrl = 'https://your-production-domain.com'; // Production

  final http.Client _client = http.Client();

  Future<bool> checkServerHealth() async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/health'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['status'] == 'healthy';
      }
      return false;
    } catch (e) {
      print('Health check failed: $e');
      return false;
    }
  }

  Future<MusicGenerationResponse> generateMusic(MusicGenerationRequest request) async {
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl/music/generate'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(request.toJson()),
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        return MusicGenerationResponse.fromJson(json.decode(response.body));
      } else {
        final error = json.decode(response.body);
        throw Exception(error['detail'] ?? 'Generation failed');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  Future<TrackStatus> getTrackStatus(String trackId) async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/music/status/$trackId'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return TrackStatus.fromJson(json.decode(response.body));
      } else if (response.statusCode == 404) {
        throw Exception('Track not found');
      } else {
        throw Exception('Failed to get track status');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  Stream<TrackStatus> pollTrackStatus(String trackId) async* {
    while (true) {
      try {
        final status = await getTrackStatus(trackId);
        yield status;
        
        if (status.status == 'completed' || status.status == 'failed') {
          break;
        }
        
        await Future.delayed(const Duration(seconds: 2));
      } catch (e) {
        throw Exception('Polling failed: $e');
      }
    }
  }

  void dispose() {
    _client.close();
  }
}
```

### **State Management (Provider/Riverpod)**

```dart
// lib/providers/music_generator_provider.dart
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/music_generator_service.dart';

final musicGeneratorServiceProvider = Provider<MusicGeneratorService>((ref) {
  return MusicGeneratorService();
});

class MusicGeneratorState {
  final bool isGenerating;
  final TrackStatus? currentTrack;
  final String? error;
  final bool isServerOnline;

  MusicGeneratorState({
    this.isGenerating = false,
    this.currentTrack,
    this.error,
    this.isServerOnline = false,
  });

  MusicGeneratorState copyWith({
    bool? isGenerating,
    TrackStatus? currentTrack,
    String? error,
    bool? isServerOnline,
  }) {
    return MusicGeneratorState(
      isGenerating: isGenerating ?? this.isGenerating,
      currentTrack: currentTrack ?? this.currentTrack,
      error: error,
      isServerOnline: isServerOnline ?? this.isServerOnline,
    );
  }
}

class MusicGeneratorNotifier extends StateNotifier<MusicGeneratorState> {
  final MusicGeneratorService _service;

  MusicGeneratorNotifier(this._service) : super(MusicGeneratorState()) {
    _checkServerHealth();
  }

  Future<void> _checkServerHealth() async {
    try {
      final isOnline = await _service.checkServerHealth();
      state = state.copyWith(isServerOnline: isOnline);
    } catch (e) {
      state = state.copyWith(isServerOnline: false);
    }
  }

  Future<void> generateMusic(String prompt, int duration) async {
    if (state.isGenerating) return;

    state = state.copyWith(
      isGenerating: true,
      error: null,
      currentTrack: null,
    );

    try {
      final request = MusicGenerationRequest(
        prompt: prompt.trim(),
        duration: duration,
      );

      final response = await _service.generateMusic(request);
      
      // Start polling for status
      _pollTrackStatus(response.trackId);
      
    } catch (e) {
      state = state.copyWith(
        isGenerating: false,
        error: e.toString(),
      );
    }
  }

  void _pollTrackStatus(String trackId) {
    _service.pollTrackStatus(trackId).listen(
      (status) {
        state = state.copyWith(currentTrack: status);
        
        if (status.status == 'completed' || status.status == 'failed') {
          state = state.copyWith(isGenerating: false);
        }
      },
      onError: (error) {
        state = state.copyWith(
          isGenerating: false,
          error: error.toString(),
        );
      },
    );
  }

  void reset() {
    state = MusicGeneratorState(isServerOnline: state.isServerOnline);
  }

  void clearError() {
    state = state.copyWith(error: null);
  }
}

final musicGeneratorProvider = StateNotifierProvider<MusicGeneratorNotifier, MusicGeneratorState>((ref) {
  final service = ref.watch(musicGeneratorServiceProvider);
  return MusicGeneratorNotifier(service);
});
```

### **Main UI Widget**

```dart
// lib/screens/music_generator_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import '../providers/music_generator_provider.dart';

class MusicGeneratorScreen extends ConsumerStatefulWidget {
  @override
  _MusicGeneratorScreenState createState() => _MusicGeneratorScreenState();
}

class _MusicGeneratorScreenState extends ConsumerState<MusicGeneratorScreen> {
  final _promptController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  double _duration = 30;

  @override
  void dispose() {
    _promptController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(musicGeneratorProvider);
    
    return CupertinoPageScaffold(
      navigationBar: const CupertinoNavigationBar(
        middle: Text('🎵 Music AI Generator'),
      ),
      child: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _buildHeader(),
              const SizedBox(height: 24),
              _buildServerStatus(state.isServerOnline),
              const SizedBox(height: 24),
              _buildGenerationForm(state),
              const SizedBox(height: 24),
              if (state.error != null) _buildErrorDisplay(state.error!),
              if (state.currentTrack != null) _buildProgressDisplay(state.currentTrack!),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Column(
      children: [
        Text(
          'Music AI Generator',
          style: CupertinoTheme.of(context).textTheme.navLargeTitleTextStyle,
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 8),
        Text(
          'Created by Sergie Code',
          style: CupertinoTheme.of(context).textTheme.textStyle.copyWith(
            color: CupertinoColors.secondaryLabel,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildServerStatus(bool isOnline) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isOnline ? CupertinoColors.systemGreen.withOpacity(0.1) : CupertinoColors.systemRed.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isOnline ? CupertinoColors.systemGreen : CupertinoColors.systemRed,
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Icon(
            isOnline ? CupertinoIcons.checkmark_circle : CupertinoIcons.xmark_circle,
            color: isOnline ? CupertinoColors.systemGreen : CupertinoColors.systemRed,
          ),
          const SizedBox(width: 8),
          Text(
            isOnline ? 'Server Online' : 'Server Offline',
            style: TextStyle(
              color: isOnline ? CupertinoColors.systemGreen : CupertinoColors.systemRed,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGenerationForm(MusicGeneratorState state) {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Prompt Input
          CupertinoTextField(
            controller: _promptController,
            placeholder: 'Describe the music you want to generate...',
            maxLines: 3,
            enabled: !state.isGenerating && state.isServerOnline,
            decoration: BoxDecoration(
              border: Border.all(color: CupertinoColors.systemGrey4),
              borderRadius: BorderRadius.circular(8),
            ),
            padding: const EdgeInsets.all(12),
          ),
          const SizedBox(height: 16),
          
          // Duration Slider
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Duration: ${_duration.round()} seconds',
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 8),
              CupertinoSlider(
                value: _duration,
                min: 5,
                max: 300,
                divisions: 59,
                onChanged: state.isGenerating ? null : (value) {
                  setState(() => _duration = value);
                },
              ),
            ],
          ),
          const SizedBox(height: 24),
          
          // Generate Button
          CupertinoButton.filled(
            onPressed: (!state.isGenerating && state.isServerOnline && _promptController.text.trim().isNotEmpty)
                ? _generateMusic
                : null,
            child: state.isGenerating
                ? const CupertinoActivityIndicator(color: CupertinoColors.white)
                : const Text('Generate Music'),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorDisplay(String error) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: CupertinoColors.systemRed.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: CupertinoColors.systemRed),
      ),
      child: Row(
        children: [
          const Icon(CupertinoIcons.exclamationmark_triangle, color: CupertinoColors.systemRed),
          const SizedBox(width: 8),
          Expanded(child: Text(error, style: const TextStyle(color: CupertinoColors.systemRed))),
          CupertinoButton(
            padding: EdgeInsets.zero,
            onPressed: () => ref.read(musicGeneratorProvider.notifier).clearError(),
            child: const Icon(CupertinoIcons.xmark, color: CupertinoColors.systemRed),
          ),
        ],
      ),
    );
  }

  Widget _buildProgressDisplay(TrackStatus track) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: CupertinoColors.systemBackground,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: CupertinoColors.systemGrey4),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'Generation Progress',
            style: CupertinoTheme.of(context).textTheme.navTitleTextStyle,
          ),
          const SizedBox(height: 16),
          
          // Track Info
          _buildInfoRow('Track ID', track.trackId),
          _buildInfoRow('Prompt', track.prompt),
          _buildInfoRow('Duration', '${track.duration} seconds'),
          _buildInfoRow('Status', track.status.toUpperCase()),
          
          const SizedBox(height: 16),
          
          // Progress Bar
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Progress: ${track.progress}%'),
              const SizedBox(height: 8),
              LinearProgressIndicator(
                value: track.progress / 100,
                backgroundColor: CupertinoColors.systemGrey5,
                valueColor: AlwaysStoppedAnimation<Color>(
                  track.status == 'completed' 
                      ? CupertinoColors.systemGreen 
                      : track.status == 'failed'
                          ? CupertinoColors.systemRed
                          : CupertinoColors.systemBlue,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Action Buttons
          if (track.status == 'completed' && track.downloadUrl != null)
            CupertinoButton.filled(
              onPressed: () => _downloadTrack(track.downloadUrl!),
              child: const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(CupertinoIcons.cloud_download, color: CupertinoColors.white),
                  SizedBox(width: 8),
                  Text('Download Track'),
                ],
              ),
            ),
          
          if (track.status == 'completed' || track.status == 'failed')
            CupertinoButton(
              onPressed: _reset,
              child: const Text('Generate Another'),
            ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }

  void _generateMusic() {
    if (_formKey.currentState?.validate() ?? false) {
      ref.read(musicGeneratorProvider.notifier).generateMusic(
        _promptController.text.trim(),
        _duration.round(),
      );
    }
  }

  void _downloadTrack(String url) async {
    if (await canLaunch(url)) {
      await launch(url);
    } else {
      _showAlert('Error', 'Could not open download link');
    }
  }

  void _reset() {
    _promptController.clear();
    setState(() => _duration = 30);
    ref.read(musicGeneratorProvider.notifier).reset();
  }

  void _showAlert(String title, String message) {
    showCupertinoDialog(
      context: context,
      builder: (context) => CupertinoAlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          CupertinoDialogAction(
            child: const Text('OK'),
            onPressed: () => Navigator.of(context).pop(),
          ),
        ],
      ),
    );
  }
}
```

### **Dependencies (pubspec.yaml)**

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # State Management
  flutter_riverpod: ^2.4.6
  
  # HTTP Client
  http: ^1.1.0
  
  # URL Launcher
  url_launcher: ^6.2.1
  
  # Cupertino Icons
  cupertino_icons: ^1.0.6

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0
```

---

## ⚠️ **Error Handling**

### **Common Error Scenarios**

```javascript
// Frontend Error Handling Examples
class APIErrorHandler {
  static handleError(error, response) {
    // Network Errors
    if (!navigator.onLine) {
      return {
        type: 'NETWORK_ERROR',
        message: 'No internet connection. Please check your network.',
        action: 'retry'
      };
    }

    // Server Errors by Status Code
    switch (response?.status) {
      case 400:
        return {
          type: 'VALIDATION_ERROR',
          message: error.detail || 'Invalid request parameters',
          action: 'fix_input'
        };

      case 404:
        return {
          type: 'NOT_FOUND',
          message: 'Track not found. It may have expired.',
          action: 'generate_new'
        };

      case 422:
        return {
          type: 'INPUT_ERROR',
          message: 'Please check your input parameters',
          details: error.detail,
          action: 'fix_input'
        };

      case 500:
        return {
          type: 'SERVER_ERROR',
          message: 'Server error. Please try again later.',
          action: 'retry_later'
        };

      default:
        return {
          type: 'UNKNOWN_ERROR',
          message: 'An unexpected error occurred',
          action: 'contact_support'
        };
    }
  }
}
```

### **Retry Logic Implementation**

```javascript
class RetryableRequest {
  static async withRetry(requestFn, maxRetries = 3, delay = 1000) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await requestFn();
      } catch (error) {
        if (attempt === maxRetries) {
          throw error;
        }
        
        // Exponential backoff
        await new Promise(resolve => 
          setTimeout(resolve, delay * Math.pow(2, attempt - 1))
        );
      }
    }
  }
}

// Usage Example
const trackStatus = await RetryableRequest.withRetry(
  () => musicClient.getTrackStatus(trackId),
  3,  // Max retries
  1000 // Initial delay (ms)
);
```

---

## 🔄 **Real-time Features**

### **WebSocket Integration (Future Enhancement)**

```javascript
// WebSocket Implementation for Real-time Updates
class MusicGeneratorWebSocket {
  constructor(baseURL) {
    this.baseURL = baseURL.replace('http', 'ws');
    this.ws = null;
    this.eventHandlers = new Map();
  }

  connect() {
    this.ws = new WebSocket(`${this.baseURL}/ws`);
    
    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.emit('connected');
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.emit(data.type, data.payload);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.emit('disconnected');
      // Auto-reconnect
      setTimeout(() => this.connect(), 5000);
    };
  }

  subscribe(trackId) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        action: 'subscribe',
        track_id: trackId
      }));
    }
  }

  on(event, handler) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event).push(handler);
  }

  emit(event, data) {
    const handlers = this.eventHandlers.get(event) || [];
    handlers.forEach(handler => handler(data));
  }
}
```

### **Server-Sent Events Alternative**

```javascript
// SSE Implementation for Progress Updates
class MusicGeneratorSSE {
  constructor(baseURL) {
    this.baseURL = baseURL;
  }

  subscribeToTrack(trackId, onProgress, onComplete, onError) {
    const eventSource = new EventSource(
      `${this.baseURL}/music/events/${trackId}`
    );

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'progress':
          onProgress(data.payload);
          break;
        case 'completed':
          onComplete(data.payload);
          eventSource.close();
          break;
        case 'failed':
          onError(data.payload);
          eventSource.close();
          break;
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      onError({ message: 'Connection lost' });
      eventSource.close();
    };

    return eventSource;
  }
}
```

---

## ⚡ **Performance Optimization**

### **Request Caching**

```javascript
// Simple Cache Implementation
class APICache {
  constructor(ttl = 300000) { // 5 minutes default
    this.cache = new Map();
    this.ttl = ttl;
  }

  set(key, value) {
    this.cache.set(key, {
      value,
      timestamp: Date.now()
    });
  }

  get(key) {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() - item.timestamp > this.ttl) {
      this.cache.delete(key);
      return null;
    }

    return item.value;
  }

  clear() {
    this.cache.clear();
  }
}

// Usage in API Client
class CachedMusicClient extends MusicGeneratorClient {
  constructor(baseURL) {
    super(baseURL);
    this.cache = new APICache();
  }

  async getTrackStatus(trackId) {
    const cacheKey = `status_${trackId}`;
    const cached = this.cache.get(cacheKey);
    
    if (cached && cached.status !== 'processing') {
      return cached;
    }

    const status = await super.getTrackStatus(trackId);
    this.cache.set(cacheKey, status);
    return status;
  }
}
```

### **Request Debouncing**

```javascript
// Debounce Function for Form Input
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Usage in Form Validation
const debouncedValidatePrompt = debounce((prompt) => {
  if (prompt.length > 0 && prompt.length < 500) {
    validatePromptOnServer(prompt);
  }
}, 500);
```

---

## 🧪 **Testing Integration**

### **API Client Testing**

```javascript
// Jest Test Example
describe('MusicGeneratorClient', () => {
  let client;
  let mockFetch;

  beforeEach(() => {
    client = new MusicGeneratorClient('http://localhost:8000');
    mockFetch = jest.fn();
    global.fetch = mockFetch;
  });

  test('should generate music successfully', async () => {
    const mockResponse = {
      success: true,
      track_id: 'track_test123',
      prompt: 'test music',
      duration: 30,
      status: 'processing'
    };

    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse)
    });

    const result = await client.generateMusic('test music', 30);
    
    expect(result.track_id).toBe('track_test123');
    expect(result.success).toBe(true);
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/music/generate',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: 'test music', duration: 30 })
      })
    );
  });

  test('should handle API errors', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 400,
      json: () => Promise.resolve({ detail: 'Invalid prompt' })
    });

    await expect(client.generateMusic('', 30))
      .rejects
      .toThrow('Invalid prompt');
  });
});
```

### **Flutter Widget Testing**

```dart
// Flutter Test Example
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mockito/mockito.dart';

class MockMusicGeneratorService extends Mock implements MusicGeneratorService {}

void main() {
  group('MusicGeneratorScreen', () {
    late MockMusicGeneratorService mockService;
    late ProviderContainer container;

    setUp(() {
      mockService = MockMusicGeneratorService();
      container = ProviderContainer(
        overrides: [
          musicGeneratorServiceProvider.overrideWithValue(mockService),
        ],
      );
    });

    testWidgets('should display generate button when server is online', (tester) async {
      when(mockService.checkServerHealth()).thenAnswer((_) async => true);

      await tester.pumpWidget(
        UncontrolledProviderScope(
          container: container,
          child: CupertinoApp(
            home: MusicGeneratorScreen(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('Generate Music'), findsOneWidget);
      expect(find.text('Server Online'), findsOneWidget);
    });

    testWidgets('should start generation when button is pressed', (tester) async {
      when(mockService.checkServerHealth()).thenAnswer((_) async => true);
      when(mockService.generateMusic(any)).thenAnswer((_) async => 
        MusicGenerationResponse(
          success: true,
          message: 'Started',
          trackId: 'test123',
          prompt: 'test',
          duration: 30,
          estimatedProcessingTime: 15,
          status: 'processing',
        ),
      );

      await tester.pumpWidget(
        UncontrolledProviderScope(
          container: container,
          child: CupertinoApp(home: MusicGeneratorScreen()),
        ),
      );

      await tester.enterText(find.byType(CupertinoTextField), 'test music');
      await tester.tap(find.text('Generate Music'));
      await tester.pump();

      verify(mockService.generateMusic(any)).called(1);
    });
  });
}
```

---

## 📚 **Additional Resources**

### **API Documentation URLs**
- **Interactive Docs**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`
- **OpenAPI Schema**: `http://127.0.0.1:8000/openapi.json`

### **Example Projects Structure**

```
music-ai-generator-frontend/ (Angular)
├── src/
│   ├── app/
│   │   ├── services/
│   │   │   └── music-generator.service.ts
│   │   ├── components/
│   │   │   ├── music-generator/
│   │   │   ├── progress-display/
│   │   │   └── error-display/
│   │   └── models/
│   │       └── music-generator.models.ts
│   └── environments/
│       ├── environment.ts
│       └── environment.prod.ts

music-ai-generator-mobile/ (Flutter)
├── lib/
│   ├── services/
│   │   └── music_generator_service.dart
│   ├── providers/
│   │   └── music_generator_provider.dart
│   ├── screens/
│   │   └── music_generator_screen.dart
│   ├── widgets/
│   │   ├── progress_display.dart
│   │   └── error_display.dart
│   └── models/
│       └── music_generator_models.dart
```

### **Environment Configuration**

```typescript
// Angular Environment
export const environment = {
  production: false,
  apiBaseUrl: 'http://127.0.0.1:8000',
  wsBaseUrl: 'ws://127.0.0.1:8000',
  apiTimeout: 30000,
  pollInterval: 2000,
  maxRetries: 3
};
```

```dart
// Flutter Environment
class AppConfig {
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000', // Android emulator
  );
  
  static const int apiTimeout = 30000;
  static const int pollInterval = 2000;
  static const int maxRetries = 3;
}
```

---

## 🚀 **Quick Start Checklist**

### **For Frontend Developers (Angular)**
- [ ] Install Angular CLI and create new project
- [ ] Add HttpClientModule to app.module.ts
- [ ] Copy MusicGeneratorService implementation
- [ ] Create music generator component with form
- [ ] Implement progress tracking UI
- [ ] Add error handling and validation
- [ ] Test with running backend server

### **For Mobile Developers (Flutter)**
- [ ] Create new Flutter project with Cupertino design
- [ ] Add dependencies: http, flutter_riverpod, url_launcher
- [ ] Implement MusicGeneratorService
- [ ] Create state management with Riverpod
- [ ] Build Cupertino-style UI screens
- [ ] Implement real-time progress updates
- [ ] Test on iOS/Android simulators

### **Backend Verification**
- [ ] Ensure backend server is running: `.\start_server.ps1`
- [ ] Verify health endpoint: `GET http://127.0.0.1:8000/health`
- [ ] Check API docs: `http://127.0.0.1:8000/docs`
- [ ] Test generation endpoint with sample request
- [ ] Confirm CORS is working for frontend domain

---

## 🎯 **Success Criteria**

Your integration is successful when:

✅ **Connection**: Frontend/mobile app connects to backend API  
✅ **Generation**: Users can submit prompts and start music generation  
✅ **Progress**: Real-time progress updates display correctly  
✅ **Completion**: Generated tracks can be downloaded/played  
✅ **Error Handling**: All error scenarios are handled gracefully  
✅ **Validation**: Input validation works on both frontend and backend  
✅ **Performance**: Smooth user experience with proper loading states  

---

**🎵 Ready to build amazing music AI applications with this comprehensive integration guide! Perfect for Sergie Code's educational content and AI tools for musicians. 🎵**

---

*This integration guide provides everything needed to build production-ready frontend and mobile applications that seamlessly connect with the Music AI Generator Backend. Use this documentation to create engaging user experiences for musicians and content creators!*
