package com.asiasalman.autoparts.ui.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.asiasalman.autoparts.data.model.Product
import com.asiasalman.autoparts.databinding.ItemProductBinding
import com.bumptech.glide.Glide

class ProductAdapter(
    private val onItemClick: (Product) -> Unit,
    private val onAddToCart: (Product, Boolean) -> Unit // isCash
) : ListAdapter<Product, ProductAdapter.ProductViewHolder>(ProductDiffCallback()) {
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ProductViewHolder {
        val binding = ItemProductBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ProductViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: ProductViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
    
    inner class ProductViewHolder(
        private val binding: ItemProductBinding
    ) : RecyclerView.ViewHolder(binding.root) {
        
        fun bind(product: Product) {
            binding.apply {
                productNameTextView.text = product.nameFa
                productBrandTextView.text = product.brand?.nameFa ?: ""
                
                // Load image
                Glide.with(root.context)
                    .load(product.imageUrl)
                    .placeholder(android.R.drawable.ic_menu_gallery)
                    .into(productImageView)
                
                // Price
                val price = product.getDisplayPrice(isCash = true)
                priceCashTextView.text = formatPrice(price)
                
                if (product.hasDiscount()) {
                    discountBadge.visibility = android.view.View.VISIBLE
                    discountBadge.text = "${product.discountPercentage?.toInt()}%"
                } else {
                    discountBadge.visibility = android.view.View.GONE
                }
                
                // Stock
                if (product.isInStock()) {
                    stockTextView.text = "موجود"
                    stockTextView.setTextColor(root.context.getColor(android.R.color.holo_green_dark))
                } else {
                    stockTextView.text = "ناموجود"
                    stockTextView.setTextColor(root.context.getColor(android.R.color.holo_red_dark))
                }
                
                // Click listeners
                root.setOnClickListener {
                    onItemClick(product)
                }
                
                addToCartButton.setOnClickListener {
                    onAddToCart(product, true) // Default to cash
                }
            }
        }
        
        private fun formatPrice(price: Int): String {
            val thousands = price / 1000
            return "$thousands هزار ریال"
        }
    }
    
    class ProductDiffCallback : DiffUtil.ItemCallback<Product>() {
        override fun areItemsTheSame(oldItem: Product, newItem: Product): Boolean {
            return oldItem.id == newItem.id
        }
        
        override fun areContentsTheSame(oldItem: Product, newItem: Product): Boolean {
            return oldItem == newItem
        }
    }
}

