package com.asiasalman.autoparts.ui.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.asiasalman.autoparts.data.model.CartItem
import com.asiasalman.autoparts.databinding.ItemCartBinding
import com.bumptech.glide.Glide

class CartItemAdapter(
    private val onQuantityChange: (CartItem, Int) -> Unit,
    private val onRemove: (CartItem) -> Unit
) : ListAdapter<CartItem, CartItemAdapter.CartItemViewHolder>(CartItemDiffCallback()) {
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CartItemViewHolder {
        val binding = ItemCartBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return CartItemViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: CartItemViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
    
    inner class CartItemViewHolder(
        private val binding: ItemCartBinding
    ) : RecyclerView.ViewHolder(binding.root) {
        
        fun bind(cartItem: CartItem) {
            binding.apply {
                productNameTextView.text = cartItem.product.nameFa
                productSkuTextView.text = cartItem.product.sku
                
                Glide.with(root.context)
                    .load(cartItem.product.imageUrl)
                    .placeholder(android.R.drawable.ic_menu_gallery)
                    .into(productImageView)
                
                quantityTextView.text = cartItem.quantity.toString()
                
                val price = cartItem.getTotalPrice(cartItem.priceType == "cash")
                totalPriceTextView.text = formatPrice(price)
                
                increaseButton.setOnClickListener {
                    onQuantityChange(cartItem, cartItem.quantity + 1)
                }
                
                decreaseButton.setOnClickListener {
                    if (cartItem.quantity > 1) {
                        onQuantityChange(cartItem, cartItem.quantity - 1)
                    }
                }
                
                removeButton.setOnClickListener {
                    onRemove(cartItem)
                }
            }
        }
        
        private fun formatPrice(price: Int): String {
            val thousands = price / 1000
            return "$thousands هزار ریال"
        }
    }
    
    class CartItemDiffCallback : DiffUtil.ItemCallback<CartItem>() {
        override fun areItemsTheSame(oldItem: CartItem, newItem: CartItem): Boolean {
            return oldItem.id == newItem.id
        }
        
        override fun areContentsTheSame(oldItem: CartItem, newItem: CartItem): Boolean {
            return oldItem == newItem
        }
    }
}

