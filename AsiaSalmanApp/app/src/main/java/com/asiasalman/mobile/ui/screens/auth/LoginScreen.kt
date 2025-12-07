package com.asiasalman.mobile.ui.screens.auth

import android.Manifest
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.scale
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.res.painterResource
import androidx.compose.foundation.Image
import androidx.compose.ui.layout.ContentScale
import com.asiasalman.mobile.R
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.asiasalman.mobile.ui.navigation.Screen
import com.asiasalman.mobile.ui.theme.*
import com.asiasalman.mobile.utils.PermissionHelper
import com.asiasalman.mobile.utils.SmsRetrieverHelper
import com.google.accompanist.permissions.ExperimentalPermissionsApi
import com.google.accompanist.permissions.rememberMultiplePermissionsState

@OptIn(ExperimentalMaterial3Api::class, ExperimentalPermissionsApi::class)
@Composable
fun LoginScreen(
    navController: NavController,
    viewModel: LoginViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current
    
    // Permission states
    val smsPermissions = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        listOf(
            Manifest.permission.READ_SMS,
            Manifest.permission.RECEIVE_SMS,
            Manifest.permission.POST_NOTIFICATIONS
        )
    } else {
        listOf(
            Manifest.permission.READ_SMS,
            Manifest.permission.RECEIVE_SMS
        )
    }
    
    val permissionsState = rememberMultiplePermissionsState(smsPermissions)
    
    // SMS Retriever
    val smsRetrieverHelper = remember { SmsRetrieverHelper(context as android.app.Activity) }
    
    // Request permissions launcher
    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val allGranted = permissions.all { it.value }
        if (allGranted) {
            // Permissions granted - will be handled by LaunchedEffect below
        }
    }
    
    // Start SMS Retriever when OTP is sent and permissions are granted
    LaunchedEffect(uiState.isOtpSent, permissionsState.allPermissionsGranted) {
        if (uiState.isOtpSent && permissionsState.allPermissionsGranted) {
            smsRetrieverHelper.startSmsRetriever().collect { otpCode ->
                otpCode?.let { code ->
                    viewModel.setOtpCodeFromSms(code)
                }
            }
        }
    }
    
    // Request permissions when OTP is sent
    LaunchedEffect(uiState.isOtpSent) {
        if (uiState.isOtpSent && !permissionsState.allPermissionsGranted) {
            permissionLauncher.launch(smsPermissions.toTypedArray())
        }
    }
    
    LaunchedEffect(uiState.isLoggedIn) {
        if (uiState.isLoggedIn) {
            navController.navigate(Screen.Shop.route) {
                popUpTo(Screen.Login.route) { inclusive = true }
            }
        }
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        // Gradient Header
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    Brush.verticalGradient(
                        colors = listOf(Primary, PrimaryDark)
                    )
                )
        ) {
            TopAppBar(
                title = {
                    Text(
                        text = if (uiState.isOtpSent) "تایید کد" else "ورود به حساب کاربری",
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                },
                navigationIcon = {
                    if (!uiState.isOtpSent) {
                        IconButton(onClick = { navController.popBackStack() }) {
                            Icon(
                                Icons.Rounded.ArrowBack,
                                contentDescription = "بازگشت",
                                modifier = Modifier.size(24.dp),
                                tint = Color.White
                            )
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color.Transparent,
                    titleContentColor = Color.White,
                    navigationIconContentColor = Color.White
                )
            )
        }
        
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // Logo Section with animation
            AnimatedVisibility(
                visible = !uiState.isOtpSent,
                enter = fadeIn(animationSpec = tween(600)) + scaleIn(
                    initialScale = 0.7f,
                    animationSpec = spring(
                        dampingRatio = Spring.DampingRatioMediumBouncy,
                        stiffness = Spring.StiffnessLow
                    )
                ),
                exit = fadeOut(animationSpec = tween(300)) + scaleOut(targetScale = 0.8f)
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    modifier = Modifier.padding(vertical = 16.dp)
                ) {
                    // App Logo with subtle pulse animation
                    val infiniteTransition = rememberInfiniteTransition(label = "logo_pulse")
                    val scale by infiniteTransition.animateFloat(
                        initialValue = 1f,
                        targetValue = 1.05f,
                        animationSpec = infiniteRepeatable(
                            animation = tween(2000, easing = FastOutSlowInEasing),
                            repeatMode = RepeatMode.Reverse
                        ),
                        label = "scale"
                    )
                    
                    Image(
                        painter = painterResource(id = R.drawable.ic_launcher_foreground),
                        contentDescription = "لوگوی آسیا سلمان",
                        modifier = Modifier
                            .size(120.dp)
                            .scale(scale)
                            .shadow(8.dp, RoundedCornerShape(24.dp)),
                        contentScale = ContentScale.Fit
                    )
                    
                    Spacer(modifier = Modifier.height(24.dp))
                    
                    // Company Name
                    Text(
                        text = "آسیا سلمان",
                        style = MaterialTheme.typography.headlineLarge,
                        fontWeight = FontWeight.Bold,
                        color = Primary,
                        textAlign = TextAlign.Center
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    // Tagline
                    Text(
                        text = "فروشگاه قطعات خودرو",
                        style = MaterialTheme.typography.bodyLarge,
                        color = TextSecondary,
                        textAlign = TextAlign.Center
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(48.dp))
            
            // Card for input section
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surface
                ),
                elevation = CardDefaults.cardElevation(4.dp)
            ) {
                Column(
                    modifier = Modifier.padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    AnimatedContent(
                        targetState = uiState.isOtpSent,
                        transitionSpec = {
                            fadeIn(
                                animationSpec = tween(300)
                            ) + slideInVertically(
                                initialOffsetY = { it / 2 },
                                animationSpec = spring(
                                    dampingRatio = Spring.DampingRatioMediumBouncy
                                )
                            ) togetherWith
                            fadeOut(
                                animationSpec = tween(200)
                            ) + slideOutVertically(
                                targetOffsetY = { -it / 2 }
                            )
                        },
                        label = "otp_screen"
                    ) { isOtpSent ->
                        if (!isOtpSent) {
                            // Phone Input Section
                            PhoneInputSection(
                                phone = uiState.phone,
                                onPhoneChange = { viewModel.updatePhone(it) },
                                onSendOtp = { viewModel.sendOtp() },
                                isLoading = uiState.isLoading,
                                error = uiState.error
                            )
                        } else {
                            // OTP Input Section
                            OtpInputSection(
                                phone = uiState.phone,
                                otpCode = uiState.otpCode,
                                onOtpChange = { viewModel.updateOtpCode(it) },
                                onVerify = { viewModel.verifyOtp() },
                                onResend = { viewModel.sendOtp() },
                                onEditPhone = { viewModel.resetOtp() },
                                isLoading = uiState.isLoading,
                                error = uiState.error,
                                resendTimer = uiState.resendTimer,
                                canResend = uiState.canResend,
                                hasSmsPermission = permissionsState.allPermissionsGranted
                            )
                        }
                    }
                }
            }
            
            // Error Message with animation
            AnimatedVisibility(
                visible = uiState.error != null,
                enter = fadeIn() + slideInVertically(
                    initialOffsetY = { -it },
                    animationSpec = spring(
                        dampingRatio = Spring.DampingRatioMediumBouncy
                    )
                ),
                exit = fadeOut() + slideOutVertically()
            ) {
                uiState.error?.let { error ->
                    Spacer(modifier = Modifier.height(20.dp))
                    Card(
                        shape = RoundedCornerShape(12.dp),
                        colors = CardDefaults.cardColors(
                            containerColor = Error.copy(alpha = 0.1f)
                        ),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Row(
                            modifier = Modifier.padding(16.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                Icons.Rounded.ErrorOutline,
                                contentDescription = null,
                                tint = Error,
                                modifier = Modifier.size(24.dp)
                            )
                            Spacer(modifier = Modifier.width(12.dp))
                            Text(
                                text = error,
                                color = Error,
                                style = MaterialTheme.typography.bodyMedium,
                                modifier = Modifier.weight(1f)
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun PhoneInputSection(
    phone: String,
    onPhoneChange: (String) -> Unit,
    onSendOtp: () -> Unit,
    isLoading: Boolean,
    error: String?
) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                Icons.Rounded.PhoneAndroid,
                contentDescription = null,
                tint = Primary,
                modifier = Modifier.size(24.dp)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = "شماره موبایل خود را وارد کنید",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurface,
                fontWeight = FontWeight.Medium
            )
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        OutlinedTextField(
            value = phone,
            onValueChange = onPhoneChange,
            modifier = Modifier.fillMaxWidth(),
            placeholder = { Text("09123456789", color = TextSecondary) },
            leadingIcon = {
                Icon(
                    Icons.Rounded.Call,
                    contentDescription = null,
                    tint = Primary
                )
            },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
            singleLine = true,
            shape = RoundedCornerShape(14.dp),
            isError = error != null,
            colors = OutlinedTextFieldDefaults.colors(
                focusedTextColor = MaterialTheme.colorScheme.onSurface,
                unfocusedTextColor = MaterialTheme.colorScheme.onSurface,
                cursorColor = Primary,
                focusedBorderColor = Primary,
                unfocusedBorderColor = CardBorder
            )
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Button(
            onClick = onSendOtp,
            modifier = Modifier
                .fillMaxWidth()
                .height(54.dp),
            enabled = !isLoading && phone.length == 11,
            shape = RoundedCornerShape(14.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = Primary,
                disabledContainerColor = Primary.copy(alpha = 0.5f)
            )
        ) {
            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(24.dp),
                    color = Color.White,
                    strokeWidth = 2.dp
                )
            } else {
                Icon(
                    Icons.Rounded.Send,
                    contentDescription = null,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "ارسال کد تایید",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Medium
                )
            }
        }
    }
}

@Composable
private fun OtpInputSection(
    phone: String,
    otpCode: String,
    onOtpChange: (String) -> Unit,
    onVerify: () -> Unit,
    onResend: () -> Unit,
    onEditPhone: () -> Unit,
    isLoading: Boolean,
    error: String?,
    resendTimer: Int,
    canResend: Boolean,
    hasSmsPermission: Boolean
) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // SMS Icon with animation
        val infiniteTransition = rememberInfiniteTransition(label = "sms_pulse")
        val alpha by infiniteTransition.animateFloat(
            initialValue = 0.7f,
            targetValue = 1f,
            animationSpec = infiniteRepeatable(
                animation = tween(1500, easing = FastOutSlowInEasing),
                repeatMode = RepeatMode.Reverse
            ),
            label = "alpha"
        )
        
        Icon(
            Icons.Rounded.Sms,
            contentDescription = null,
            modifier = Modifier
                .size(48.dp)
                .alpha(alpha),
            tint = Primary
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = "کد تایید ارسال شده به",
            style = MaterialTheme.typography.bodyLarge,
            color = TextSecondary
        )
        Text(
            text = phone,
            style = MaterialTheme.typography.titleMedium,
            color = Primary,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = "را وارد کنید",
            style = MaterialTheme.typography.bodyLarge,
            color = TextSecondary
        )
        
        if (hasSmsPermission) {
            Spacer(modifier = Modifier.height(8.dp))
            // Success message with animation
            AnimatedVisibility(
                visible = hasSmsPermission,
                enter = fadeIn(animationSpec = tween(500), initialAlpha = 0.3f)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        Icons.Rounded.CheckCircle,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp),
                        tint = Success
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "کد به صورت خودکار وارد می‌شود",
                        style = MaterialTheme.typography.bodySmall,
                        color = Success,
                        textAlign = TextAlign.Center
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        OutlinedTextField(
            value = otpCode,
            onValueChange = onOtpChange,
            modifier = Modifier.fillMaxWidth(),
            placeholder = { Text("کد تایید", color = TextSecondary) },
            leadingIcon = {
                Icon(
                    Icons.Rounded.Lock,
                    contentDescription = null,
                    tint = Primary
                )
            },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            singleLine = true,
            shape = RoundedCornerShape(14.dp),
            isError = error != null,
            colors = OutlinedTextFieldDefaults.colors(
                focusedTextColor = MaterialTheme.colorScheme.onSurface,
                unfocusedTextColor = MaterialTheme.colorScheme.onSurface,
                cursorColor = Primary,
                focusedBorderColor = Primary,
                unfocusedBorderColor = CardBorder
            )
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Button(
            onClick = onVerify,
            modifier = Modifier
                .fillMaxWidth()
                .height(54.dp),
            enabled = !isLoading && otpCode.length >= 4,
            shape = RoundedCornerShape(14.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = Primary,
                disabledContainerColor = Primary.copy(alpha = 0.5f)
            )
        ) {
            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(24.dp),
                    color = Color.White,
                    strokeWidth = 2.dp
                )
            } else {
                Icon(
                    Icons.Rounded.CheckCircle,
                    contentDescription = null,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "تایید و ورود",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Medium
                )
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            TextButton(onClick = onEditPhone) {
                Icon(
                    Icons.Rounded.Edit,
                    contentDescription = null,
                    modifier = Modifier.size(18.dp),
                    tint = Primary
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text(
                    "ویرایش شماره",
                    color = Primary
                )
            }
            
            TextButton(
                onClick = onResend,
                enabled = canResend && !isLoading
            ) {
                if (resendTimer > 0) {
                    Text(
                        "ارسال مجدد ($resendTimer)",
                        color = TextSecondary
                    )
                } else {
                    Icon(
                        Icons.Rounded.Refresh,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp),
                        tint = if (canResend) Primary else TextSecondary
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        "ارسال مجدد",
                        color = if (canResend) Primary else TextSecondary
                    )
                }
            }
        }
    }
}
