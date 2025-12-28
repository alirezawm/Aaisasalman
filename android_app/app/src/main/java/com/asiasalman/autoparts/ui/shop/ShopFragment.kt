package com.asiasalman.autoparts.ui.shop

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.asiasalman.autoparts.databinding.FragmentShopBinding
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class ShopFragment : Fragment() {
    
    private var _binding: FragmentShopBinding? = null
    private val binding get() = _binding!!
    private val viewModel: ShopViewModel by viewModels()
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentShopBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        setupSearch()
        setupRecyclerView()
        observeViewModel()
        loadProducts()
    }
    
    private fun setupSearch() {
        // TODO: Setup search functionality
    }
    
    private fun setupRecyclerView() {
        // TODO: Setup products RecyclerView
    }
    
    private fun observeViewModel() {
        // TODO: Observe ViewModel
    }
    
    private fun loadProducts() {
        viewModel.loadProducts()
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

