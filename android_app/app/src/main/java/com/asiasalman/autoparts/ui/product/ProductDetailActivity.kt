package com.asiasalman.autoparts.ui.product

import android.os.Bundle
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.asiasalman.autoparts.databinding.ActivityProductDetailBinding
import com.asiasalman.autoparts.data.model.Product
import com.asiasalman.autoparts.ui.cart.CartViewModel
import androidx.lifecycle.ViewModelProvider
import com.bumptech.glide.Glide
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class ProductDetailActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityProductDetailBinding
    private lateinit var viewModel: ProductDetailViewModel
    private lateinit var cartViewModel: CartViewModel
    
    private var product: Product? = null
    private var isCashPrice = true
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityProductDetailBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        val productId = intent.getIntExtra("product_id", -1)
        if (productId == -1) {
            finish()
            return
        }
        
        viewModel = ViewModelProvider(this)[ProductDetailViewModel::class.java]
        cartViewModel = ViewModelProvider(this)[CartViewModel::class.java]
        
        setupViews()
        observeViewModel()
        viewModel.loadProduct(productId)
    }
    
    private fun setupViews() {
        binding.apply {
            toolbar.setNavigationOnClickListener {
                finish()
            }
            
            priceTypeSwitch.setOnCheckedChangeListener { _, isChecked ->
                isCashPrice = isChecked
                updatePrice()
            }
            
            addToCartButton.setOnClickListener {
                product?.let { p ->
                    val quantity = quantityEditText.text.toString().toIntOrNull() ?: 1
                    cartViewModel.addToCart(
                        p.id,
                        quantity,
                        if (isCashPrice) "cash" else "check"
                    )
                }
            }
            
            increaseQuantityButton.setOnClickListener {
                val current = quantityEditText.text.toString().toIntOrNull() ?: 1
                quantityEditText.setText((current + 1).toString())
            }
            
            decreaseQuantityButton.setOnClickListener {
                val current = quantityEditText.text.toString().toIntOrNull() ?: 1
                if (current > 1) {
                    quantityEditText.setText((current - 1).toString())
                }
            }
        }
    }
    
    private fun observeViewModel() {
        viewModel.product.observe(this) { product ->
            product?.let {
                this.product = it
                displayProduct(it)
            }
        }
        
        viewModel.error.observe(this) { error ->
            error?.let {
                Toast.makeText(this, it, Toast.LENGTH_SHORT).show()
            }
        }
        
        cartViewModel.cartAdded.observe(this) { success ->
            if (success) {
                Toast.makeText(this, "به سبد خرید اضافه شد", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun displayProduct(product: Product) {
        binding.apply {
            productNameTextView.text = product.nameFa
            productSkuTextView.text = "کد: ${product.sku}"
            productOemTextView.text = product.oemCode?.let { "OEM: $it" } ?: ""
            productDescriptionTextView.text = product.descriptionFa ?: product.description ?: ""
            
            Glide.with(this@ProductDetailActivity)
                .load(product.imageUrl)
                .into(productImageView)
            
            stockTextView.text = if (product.isInStock()) {
                "موجود (${product.stockQuantity} عدد)"
            } else {
                "ناموجود"
            }
            
            if (product.hasDiscount()) {
                discountBadge.visibility = android.view.View.VISIBLE
                discountBadge.text = "${product.discountPercentage?.toInt()}% تخفیف"
            } else {
                discountBadge.visibility = android.view.View.GONE
            }
            
            updatePrice()
        }
    }
    
    private fun updatePrice() {
        product?.let { p ->
            val price = p.getDisplayPrice(isCashPrice)
            binding.priceTextView.text = formatPrice(price)
            binding.priceTypeTextView.text = if (isCashPrice) "قیمت نقدی" else "قیمت چکی"
        }
    }
    
    private fun formatPrice(price: Int): String {
        val thousands = price / 1000
        return "$thousands هزار ریال"
    }
}

