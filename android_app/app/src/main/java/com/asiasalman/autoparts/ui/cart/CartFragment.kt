package com.asiasalman.autoparts.ui.cart

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.asiasalman.autoparts.databinding.FragmentCartBinding
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class CartFragment : Fragment() {
    
    private var _binding: FragmentCartBinding? = null
    private val binding get() = _binding!!
    private val viewModel: CartViewModel by viewModels()
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentCartBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        setupTabs()
        setupRecyclerViews()
        observeViewModel()
        loadCart()
    }
    
    private fun setupTabs() {
        // TODO: Setup TabLayout for cash/check
    }
    
    private fun setupRecyclerViews() {
        // TODO: Setup RecyclerViews for cart items
    }
    
    private fun observeViewModel() {
        // TODO: Observe ViewModel
    }
    
    private fun loadCart() {
        viewModel.loadCart()
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

