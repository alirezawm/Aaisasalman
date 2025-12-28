package com.asiasalman.autoparts.ui.auth

import android.content.Intent
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.asiasalman.autoparts.R
import com.asiasalman.autoparts.databinding.ActivityLoginBinding
import com.asiasalman.autoparts.ui.main.MainActivity
import com.asiasalman.autoparts.ui.profile.ProfileCompletionActivity
import com.asiasalman.autoparts.util.PhoneNumberValidator
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class LoginActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityLoginBinding
    private val viewModel: LoginViewModel by viewModels()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupViews()
        observeViewModel()
    }
    
    private fun setupViews() {
        binding.phoneEditText.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                binding.sendOtpButton.isEnabled = PhoneNumberValidator.isValid(s.toString())
            }
        })
        
        binding.sendOtpButton.setOnClickListener {
            val phone = binding.phoneEditText.text.toString()
            if (PhoneNumberValidator.isValid(phone)) {
                viewModel.sendOTP(phone)
            } else {
                Toast.makeText(this, R.string.invalid_phone, Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun observeViewModel() {
        viewModel.otpSent.observe(this) { success ->
            if (success) {
                val phone = binding.phoneEditText.text.toString()
                val intent = Intent(this, OTPVerificationActivity::class.java)
                intent.putExtra("phone", phone)
                startActivity(intent)
            }
        }
        
        viewModel.error.observe(this) { error ->
            error?.let {
                Toast.makeText(this, it, Toast.LENGTH_SHORT).show()
            }
        }
        
        viewModel.loading.observe(this) { isLoading ->
            binding.sendOtpButton.isEnabled = !isLoading
            binding.progressBar.visibility = if (isLoading) android.view.View.VISIBLE else android.view.View.GONE
        }
    }
}

