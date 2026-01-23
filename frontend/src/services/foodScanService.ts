import api from './api';
import type { 
  FoodScan, 
  FoodScanResult, 
  MealType,
  ApiResponse 
} from '@/types';

export interface ScanImageData {
  image_base64: string;
  meal_type?: MealType;
}

export interface ScanBarcodeData {
  barcode: string;
}

export interface ConfirmScanData {
  result_id: number;
  confirmed_name?: string;
  confirmed_portion?: number;
  meal_type: MealType;
  log_date: string;
}

export const foodScanService = {
  // Image scanning
  async scanImage(data: ScanImageData): Promise<{
    scan: FoodScan;
    results: FoodScanResult[];
  }> {
    const response = await api.post<ApiResponse<{
      scan: FoodScan;
      results: FoodScanResult[];
    }>>('/food-scan/image', data);
    return response.data.data;
  },

  // Barcode scanning
  async scanBarcode(data: ScanBarcodeData): Promise<{
    scan: FoodScan;
    results: FoodScanResult[];
  }> {
    const response = await api.post<ApiResponse<{
      scan: FoodScan;
      results: FoodScanResult[];
    }>>('/food-scan/barcode', data);
    return response.data.data;
  },

  // Confirm and add to log
  async confirmScan(data: ConfirmScanData): Promise<{
    nutrition_log_id: number;
    message: string;
  }> {
    const response = await api.post<ApiResponse<{
      nutrition_log_id: number;
      message: string;
    }>>('/food-scan/confirm', data);
    return response.data.data;
  },

  // Get scan history
  async getScanHistory(limit = 20): Promise<FoodScan[]> {
    const response = await api.get<ApiResponse<FoodScan[]>>('/food-scan/history', {
      params: { limit },
    });
    return response.data.data;
  },

  // Get scan by ID
  async getScan(id: number): Promise<{
    scan: FoodScan;
    results: FoodScanResult[];
  }> {
    const response = await api.get<ApiResponse<{
      scan: FoodScan;
      results: FoodScanResult[];
    }>>(`/food-scan/${id}`);
    return response.data.data;
  },

  // Delete scan
  async deleteScan(id: number): Promise<void> {
    await api.delete(`/food-scan/${id}`);
  },

  // Utility: Convert file to base64
  async fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const result = reader.result as string;
        // Remove the data URL prefix (e.g., "data:image/jpeg;base64,")
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = (error) => reject(error);
    });
  },

  // Utility: Compress image before upload
  async compressImage(file: File, maxWidth = 1024, quality = 0.8): Promise<string> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');

      img.onload = () => {
        let { width, height } = img;
        
        if (width > maxWidth) {
          height = (height * maxWidth) / width;
          width = maxWidth;
        }

        canvas.width = width;
        canvas.height = height;

        ctx?.drawImage(img, 0, 0, width, height);
        
        const dataUrl = canvas.toDataURL('image/jpeg', quality);
        const base64 = dataUrl.split(',')[1];
        resolve(base64);
      };

      img.onerror = reject;
      img.src = URL.createObjectURL(file);
    });
  },
};

export default foodScanService;
