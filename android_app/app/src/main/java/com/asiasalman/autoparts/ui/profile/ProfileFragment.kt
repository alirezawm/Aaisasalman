package com.asiasalman.autoparts.ui.profile

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.asiasalman.autoparts.databinding.FragmentProfileBinding
import com.asiasalman.autoparts.ui.auth.LoginActivity
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class ProfileFragment : Fragment() {
    
    private var _binding: FragmentProfileBinding? = null
    private val binding get() = _binding!!
    private val viewModel: ProfileViewModel by viewModels()
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentProfileBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        setupViews()
        observeViewModel()
        loadProfile()
    }
    
    private fun setupViews() {
        binding.editProfileButton.setOnClickListener {
            // TODO: Navigate to edit profile
        }
        
        binding.wholesaleRequestButton.setOnClickListener {
            // TODO: Show wholesale request dialog
        }
        
        binding.logoutButton.setOnClickListener {
            viewModel.logout()
        }
    }
    
    private fun observeViewModel() {
        viewModel.user.observe(viewLifecycleOwner) { user ->
            user?.let {
                binding.fullNameTextView.text = it.fullName
                binding.phoneTextView.text = it.phone
                binding.emailTextView.text = it.email ?: "-"
                binding.companyNameTextView.text = it.companyName ?: "-"
            }
        }
        
        viewModel.loggedOut.observe(viewLifecycleOwner) { loggedOut ->
            if (loggedOut) {
                val intent = Intent(requireContext(), LoginActivity::class.java)
                intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                startActivity(intent)
                requireActivity().finish()
            }
        }
    }
    
    private fun loadProfile() {
        viewModel.loadProfile()
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

