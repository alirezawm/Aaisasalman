package com.asiasalman.autoparts.ui.auth

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.asiasalman.autoparts.databinding.ActivityOtpVerificationBinding
import com.asiasalman.autoparts.ui.main.MainActivity
import com.asiasalman.autoparts.ui.profile.ProfileCompletionActivity
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class OTPVerificationActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityOtpVerificationBinding
    private val viewModel: OTPVerificationViewModel by viewModels()
    private var phone: String = ""
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityOtpVerificationBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        phone = intent.getStringExtra("phone") ?: ""
        binding.phoneTextView.text = phone
        
        setupViews()
        observeViewModel()
    }
    
    private fun setupViews() {
        binding.verifyButton.setOnClickListener {
            val otpCode = binding.otpEditText.text.toString()
            if (otpCode.length == 6) {
                viewModel.verifyOTP(phone, otpCode)
            } else {
                Toast.makeText(this, "لطفاً کد 6 رقمی را وارد کنید", Toast.LENGTH_SHORT).show()
            }
        }
        
        binding.resendButton.setOnClickListener {
            viewModel.resendOTP(phone)
        }
    }
    
    private fun observeViewModel() {
        viewModel.verificationSuccess.observe(this) { authResponse ->
            authResponse?.let {
                // Check if profile is complete
                if (it.user.profileCompletionPercentage < 100) {
                    val intent = Intent(this, ProfileCompletionActivity::class.java)
                    intent.putExtra("user", it.user)
                    startActivity(intent)
                } else {
                    val intent = Intent(this, MainActivity::class.java)
                    startActivity(intent)
                }
                finish()
            }
        }
        
        viewModel.error.observe(this) { error ->
            error?.let {
                Toast.makeText(this, it, Toast.LENGTH_SHORT).show()
            }
        }
        
        viewModel.loading.observe(this) { isLoading ->
            binding.verifyButton.isEnabled = !isLoading
            binding.progressBar.visibility = if (isLoading) android.view.View.VISIBLE else android.view.View.GONE
        }
        
        viewModel.otpResent.observe(this) { success ->
            if (success) {
                Toast.makeText(this, "کد تایید مجدداً ارسال شد", Toast.LENGTH_SHORT).show()
            }
        }
    }
}

