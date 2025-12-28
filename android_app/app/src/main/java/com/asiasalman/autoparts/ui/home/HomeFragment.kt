package com.asiasalman.autoparts.ui.home

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.asiasalman.autoparts.databinding.FragmentHomeBinding
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class HomeFragment : Fragment() {
    
    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!
    private val viewModel: HomeViewModel by viewModels()
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHomeBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        setupRecyclerViews()
        observeViewModel()
        loadData()
    }
    
    private fun setupRecyclerViews() {
        // TODO: Setup RecyclerViews for banners, discounted products, categories
    }
    
    private fun observeViewModel() {
        // TODO: Observe ViewModel LiveData
    }
    
    private fun loadData() {
        viewModel.loadHomeData()
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

