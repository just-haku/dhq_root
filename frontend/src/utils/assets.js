/**
 * Utility for handling spritesheets and assets in the Arcade
 */

/**
 * Draws a specific frame from a spritesheet onto a canvas context
 * @param {CanvasRenderingContext2D} ctx - The canvas context
 * @param {HTMLImageElement} img - The spritesheet image
 * @param {number} x - Target x position
 * @param {number} y - Target y position
 * @param {number} width - Target width
 * @param {number} height - Target height
 * @param {number} frameIndex - Current frame index (0-based)
 * @param {number} frameWidth - Width of a single frame in the sheet
 * @param {number} frameHeight - Height of a single frame in the sheet
 * @param {number} cols - Number of columns in the spritesheet
 */
export const drawSprite = (ctx, img, x, y, width, height, frameIndex, frameWidth, frameHeight, cols = 1) => {
    if (!img.complete || img.naturalWidth === 0) return;

    const col = frameIndex % cols;
    const row = Math.floor(frameIndex / cols);

    ctx.drawImage(
        img,
        col * frameWidth,
        row * frameHeight,
        frameWidth,
        frameHeight,
        x,
        y,
        width,
        height
    );
};

/**
 * Loads an image and returns a promise
 * @param {string} src 
 * @returns {Promise<HTMLImageElement>}
 */
export const loadImage = (src) => {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = reject;
        img.src = src;
    });
};
