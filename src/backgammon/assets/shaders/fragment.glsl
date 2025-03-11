#version 300 es
precision mediump float;
uniform sampler2D Texture;

out vec4 color;
in vec2 v_text;

void main() {
  // Define the center of the texture
  vec2 center = vec2(0.5, 0.5);
  // Calculate the offset from the center
  vec2 off_center = v_text - center;

  // Apply a non-linear distortion to the offset
  off_center *= 1.0 + 0.3 * pow(abs(off_center.yx), vec2(2.5));

  // Compute new, distorted texture coordinates
  vec2 v_text2 = center + off_center;

  // Define a border margin for the smoothing effect (in texture coordinate space)
  float border = 0.05;

  // Smoothly fade near edges
  float xFade = smoothstep(0.0, border, v_text2.x) * smoothstep(0.0, border, 1.0 - v_text2.x);
  float yFade = smoothstep(0.0, border, v_text2.y) * smoothstep(0.0, border, 1.0 - v_text2.y);
  float edgeFactor = xFade * yFade;

  if (edgeFactor <= 0.0) {
    color = vec4(0.0, 0.0, 0.0, 1.0);
  } else {
    // Sample the texture at the distorted coordinates
    vec4 texColor = vec4(texture(Texture, v_text2).rgb, 1.0);

    // Modify scanline effect: Use a thickness factor to increase the width of the dark regions.
    // A thicknessFactor < 1.0 makes the scanlines thicker by reducing the frequency.
    float thicknessFactor = 0.1; // Adjust this value: lower makes scanlines thicker
    float fv = fract(v_text2.y * float(textureSize(Texture, 0).y) * thicknessFactor);

    // Use min to create a symmetric ramp for scanline brightness modulation
    fv = min(1.0, 0.8 + 0.5 * min(fv, 1.0 - fv));
    texColor.rgb *= fv;

    // Blend the texture color with black by multiplying with the edgeFactor
    color = texColor * edgeFactor;
  }
}
