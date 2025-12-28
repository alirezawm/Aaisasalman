package com.asiasalman.autoparts.ui.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.asiasalman.autoparts.data.remote.Banner
import com.asiasalman.autoparts.databinding.ItemBannerBinding
import com.bumptech.glide.Glide

class BannerAdapter(
    private val banners: List<Banner>,
    private val onBannerClick: (Banner) -> Unit
) : RecyclerView.Adapter<BannerAdapter.BannerViewHolder>() {
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): BannerViewHolder {
        val binding = ItemBannerBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return BannerViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: BannerViewHolder, position: Int) {
        holder.bind(banners[position])
    }
    
    override fun getItemCount() = banners.size
    
    inner class BannerViewHolder(
        private val binding: ItemBannerBinding
    ) : RecyclerView.ViewHolder(binding.root) {
        
        fun bind(banner: Banner) {
            Glide.with(binding.root.context)
                .load(banner.imageUrl)
                .centerCrop()
                .into(binding.bannerImageView)
            
            binding.bannerTitleTextView.text = banner.titleFa
            
            binding.root.setOnClickListener {
                onBannerClick(banner)
            }
        }
    }
}

