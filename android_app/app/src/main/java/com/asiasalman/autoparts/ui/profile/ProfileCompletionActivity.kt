package com.asiasalman.autoparts.ui.profile

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.asiasalman.autoparts.databinding.ActivityProfileCompletionBinding
import com.asiasalman.autoparts.data.model.User
import com.asiasalman.autoparts.ui.main.MainActivity
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class ProfileCompletionActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityProfileCompletionBinding
    private val viewModel: ProfileCompletionViewModel by viewModels()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityProfileCompletionBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupViews()
        observeViewModel()
    }
    
    private fun setupViews() {
        binding.saveButton.setOnClickListener {
            val fullName = binding.fullNameEditText.text.toString()
            val email = binding.emailEditText.text.toString()
            val companyName = binding.companyNameEditText.text.toString()
            
            if (fullName.isNotEmpty()) {
                viewModel.updateProfile(fullName, email, companyName)
            } else {
                Toast.makeText(this, "نام و نام خانوادگی الزامی است", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun observeViewModel() {
        viewModel.profileUpdated.observe(this) { success ->
            if (success) {
                val intent = Intent(this, MainActivity::class.java)
                startActivity(intent)
                finish()
            }
        }
        
        viewModel.error.observe(this) { error ->
            error?.let {
                Toast.makeText(this, it, Toast.LENGTH_SHORT).show()
            }
        }
    }
}

