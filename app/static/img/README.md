# SetFit Gym - Image Assets

## Hero Slider Images

For optimal performance and visual appeal, add the following gym images to this directory:

### Required Images:
1. **hero-gym-1.jpg** - Modern gym equipment area (1920x1080px or higher)
2. **hero-gym-2.jpg** - Group fitness class or training session (1920x1080px or higher)
3. **hero-gym-3.jpg** - Outdoor activity (trekking/mountain scene) (1920x1080px or higher)
4. **hero-gym-4.jpg** - Cricket or sports activity (1920x1080px or higher)

### Image Guidelines:
- **Format**: JPG or WebP for best compression
- **Resolution**: Minimum 1920x1080px (Full HD)
- **Aspect Ratio**: 16:9 preferred
- **File Size**: Optimize to under 500KB per image
- **Orientation**: Landscape
- **Focus**: Show active fitness, community, and energy

### Current Setup:
The hero slider currently uses Unsplash CDN images as placeholders:
- Gym equipment and weights
- Fitness class activities
- Modern gym interior
- Training and workout scenes

### To Replace with Local Images:
1. Add your optimized images to this directory
2. Update the hero-slide URLs in `templates/index.html`:
   ```html
   <div class="hero-slide" style="background-image: url('{{ url_for('static', filename='img/hero-gym-1.jpg') }}');"></div>
   ```

### Optimization Tips:
- Use tools like TinyPNG or ImageOptim to compress images
- Consider using WebP format for better compression (with JPG fallback)
- Use responsive images with srcset for different screen sizes
- Add lazy loading for images below the fold

### Additional Assets:
- **logo.png** - SetFit Gym logo (transparent background)
- **favicon.ico** - Browser tab icon
- **og-image.jpg** - Social media preview image (1200x630px)

## Activity Section Images

Additional images to enhance the activity sections:
- **trekking-1.jpg** - Scenic mountain trekking scene
- **trekking-2.jpg** - Group trekking activity
- **cricket-1.jpg** - Cricket match or practice
- **cricket-2.jpg** - Cricket tournament action

## Brand Assets

- **logo-light.svg** - Logo for dark backgrounds
- **logo-dark.svg** - Logo for light backgrounds
- **icon-192.png** - PWA icon (192x192px)
- **icon-512.png** - PWA icon (512x512px)

---

**Note**: All images should be properly licensed for commercial use. Ensure you have rights to use any images in production.
