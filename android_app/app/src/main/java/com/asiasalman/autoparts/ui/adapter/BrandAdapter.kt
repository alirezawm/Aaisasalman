package com.asiasalman.autoparts.ui.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.asiasalman.autoparts.data.model.Brand
import com.asiasalman.autoparts.databinding.ItemBrandBinding
import com.bumptech.glide.Glide

class BrandAdapter(
    private val onItemClick: (Brand) -> Unit
) : ListAdapter<Brand, BrandAdapter.BrandViewHolder>(BrandDiffCallback()) {
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): BrandViewHolder {
        val binding = ItemBrandBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return BrandViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: BrandViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
    
    inner class BrandViewHolder(
        private val binding: ItemBrandBinding
    ) : RecyclerView.ViewHolder(binding.root) {
        
        fun bind(brand: Brand) {
            binding.brandNameTextView.text = brand.nameFa
            
            brand.logoUrl?.let { logoUrl ->
                Glide.with(binding.root.context)
                    .load(logoUrl)
                    .placeholder(android.R.drawable.ic_menu_gallery)
                    .into(binding.brandLogoImageView)
            }
            
            binding.root.setOnClickListener {
                onItemClick(brand)
            }
        }
    }
    
    class BrandDiffCallback : DiffUtil.ItemCallback<Brand>() {
        override fun areItemsTheSame(oldItem: Brand, newItem: Brand): Boolean {
            return oldItem.id == newItem.id
        }
        
        override fun areContentsTheSame(oldItem: Brand, newItem: Brand): Boolean {
            return oldItem == newItem
        }
    }
}

