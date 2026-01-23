import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { foodScanService } from '@/services';
import { Card, Button, LoadingSpinner } from '@/components/ui';
import { FoodScanResult, MealType } from '@/types';
import { format } from 'date-fns';
import {
  CameraIcon,
  PhotoIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const mealTypes: { key: MealType; label: string }[] = [
  { key: 'breakfast', label: '🌅 Breakfast' },
  { key: 'lunch', label: '☀️ Lunch' },
  { key: 'dinner', label: '🌙 Dinner' },
  { key: 'snacks', label: '🍿 Snacks' },
];

export const FoodScanPage: React.FC = () => {
  const [isScanning, setIsScanning] = useState(false);
  const [scanResults, setScanResults] = useState<FoodScanResult[]>([]);
  const [selectedResult, setSelectedResult] = useState<FoodScanResult | null>(null);
  const [selectedMeal, setSelectedMeal] = useState<MealType>('lunch');
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const [scanComplete, setScanComplete] = useState(false);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Show preview
    const reader = new FileReader();
    reader.onload = () => {
      setPreviewImage(reader.result as string);
    };
    reader.readAsDataURL(file);

    // Scan image
    setIsScanning(true);
    setScanComplete(false);
    
    try {
      const base64 = await foodScanService.compressImage(file);
      const result = await foodScanService.scanImage({
        image_base64: base64,
        meal_type: selectedMeal,
      });
      
      setScanResults(result.results);
      if (result.results.length > 0) {
        setSelectedResult(result.results[0]);
      }
      setScanComplete(true);
      toast.success('Food recognized!');
    } catch {
      toast.error('Failed to scan food. Please try again.');
    } finally {
      setIsScanning(false);
    }
  }, [selectedMeal]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp'],
    },
    maxFiles: 1,
    disabled: isScanning,
  });

  const handleConfirm = async () => {
    if (!selectedResult) return;

    try {
      await foodScanService.confirmScan({
        result_id: selectedResult.id,
        meal_type: selectedMeal,
        log_date: format(new Date(), 'yyyy-MM-dd'),
      });
      
      toast.success('Food added to your log!');
      
      // Reset
      setScanResults([]);
      setSelectedResult(null);
      setPreviewImage(null);
      setScanComplete(false);
    } catch {
      toast.error('Failed to add food');
    }
  };

  const handleReset = () => {
    setScanResults([]);
    setSelectedResult(null);
    setPreviewImage(null);
    setScanComplete(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-secondary-900">📸 Scan Food</h1>
        <p className="text-secondary-500">Take a photo or upload an image of your food</p>
      </div>

      {/* Meal Type Selection */}
      <Card>
        <p className="text-sm font-medium text-secondary-700 mb-3">Adding to:</p>
        <div className="flex gap-2 flex-wrap">
          {mealTypes.map((meal) => (
            <button
              key={meal.key}
              onClick={() => setSelectedMeal(meal.key)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedMeal === meal.key
                  ? 'bg-primary-500 text-white'
                  : 'bg-secondary-100 text-secondary-700 hover:bg-secondary-200'
              }`}
            >
              {meal.label}
            </button>
          ))}
        </div>
      </Card>

      {/* Upload Area */}
      {!previewImage && (
        <Card padding="lg">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-primary-500 bg-primary-50'
                : 'border-secondary-300 hover:border-primary-400'
            }`}
          >
            <input {...getInputProps()} />
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-4">
                {isDragActive ? (
                  <PhotoIcon className="w-8 h-8 text-primary-600" />
                ) : (
                  <CameraIcon className="w-8 h-8 text-primary-600" />
                )}
              </div>
              <p className="text-lg font-medium text-secondary-900 mb-1">
                {isDragActive ? 'Drop your image here' : 'Take or upload a food photo'}
              </p>
              <p className="text-secondary-500">
                Drag & drop or click to select
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Preview & Results */}
      {previewImage && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Image Preview */}
          <Card>
            <div className="relative">
              <img
                src={previewImage}
                alt="Food preview"
                className="w-full h-64 object-cover rounded-lg"
              />
              {isScanning && (
                <div className="absolute inset-0 bg-black/50 rounded-lg flex items-center justify-center">
                  <div className="text-center text-white">
                    <LoadingSpinner size="lg" color="text-white" />
                    <p className="mt-2">Analyzing food...</p>
                  </div>
                </div>
              )}
            </div>
            <Button
              variant="ghost"
              className="w-full mt-4"
              onClick={handleReset}
            >
              Take another photo
            </Button>
          </Card>

          {/* Results */}
          {scanComplete && (
            <Card>
              <h3 className="font-semibold text-secondary-900 mb-4">
                Detected Foods
              </h3>
              
              {scanResults.length > 0 ? (
                <>
                  <div className="space-y-3 mb-4">
                    {scanResults.map((result) => (
                      <button
                        key={result.id}
                        onClick={() => setSelectedResult(result)}
                        className={`w-full text-left p-4 rounded-lg border transition-colors ${
                          selectedResult?.id === result.id
                            ? 'border-primary-500 bg-primary-50'
                            : 'border-secondary-200 hover:bg-secondary-50'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-medium text-secondary-900">
                              {result.food_name}
                            </p>
                            {result.brand && (
                              <p className="text-sm text-secondary-500">
                                {result.brand}
                              </p>
                            )}
                            <p className="text-sm text-secondary-500 mt-1">
                              {result.estimated_calories} kcal • 
                              {result.estimated_portion || 'Standard portion'}
                            </p>
                          </div>
                          <div className="text-right">
                            <span className="text-sm font-medium text-primary-600">
                              {Math.round(result.confidence * 100)}% match
                            </span>
                            {selectedResult?.id === result.id && (
                              <CheckCircleIcon className="w-5 h-5 text-primary-500 mt-1" />
                            )}
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>

                  {selectedResult && (
                    <div className="border-t pt-4">
                      <h4 className="text-sm font-medium text-secondary-700 mb-2">
                        Nutrition (estimated)
                      </h4>
                      <div className="grid grid-cols-4 gap-2 text-center mb-4">
                        <div className="bg-secondary-50 p-2 rounded">
                          <p className="text-lg font-bold">{selectedResult.estimated_calories}</p>
                          <p className="text-xs text-secondary-500">kcal</p>
                        </div>
                        <div className="bg-blue-50 p-2 rounded">
                          <p className="text-lg font-bold text-blue-600">
                            {selectedResult.estimated_protein_g}g
                          </p>
                          <p className="text-xs text-secondary-500">Protein</p>
                        </div>
                        <div className="bg-orange-50 p-2 rounded">
                          <p className="text-lg font-bold text-orange-600">
                            {selectedResult.estimated_carbs_g}g
                          </p>
                          <p className="text-xs text-secondary-500">Carbs</p>
                        </div>
                        <div className="bg-purple-50 p-2 rounded">
                          <p className="text-lg font-bold text-purple-600">
                            {selectedResult.estimated_fat_g}g
                          </p>
                          <p className="text-xs text-secondary-500">Fat</p>
                        </div>
                      </div>

                      <Button onClick={handleConfirm} className="w-full">
                        Add to {mealTypes.find((m) => m.key === selectedMeal)?.label}
                      </Button>
                    </div>
                  )}
                </>
              ) : (
                <div className="text-center py-8">
                  <p className="text-secondary-500 mb-4">
                    Couldn't identify any food in this image.
                  </p>
                  <Button variant="outline" onClick={handleReset}>
                    Try again
                  </Button>
                </div>
              )}
            </Card>
          )}
        </div>
      )}

      {/* Tips */}
      <Card>
        <h3 className="font-semibold text-secondary-900 mb-3">📷 Tips for best results</h3>
        <ul className="space-y-2 text-secondary-600">
          <li className="flex items-start gap-2">
            <span>•</span>
            <span>Take photos in good lighting</span>
          </li>
          <li className="flex items-start gap-2">
            <span>•</span>
            <span>Center the food in the frame</span>
          </li>
          <li className="flex items-start gap-2">
            <span>•</span>
            <span>Avoid blurry images</span>
          </li>
          <li className="flex items-start gap-2">
            <span>•</span>
            <span>Single items work best</span>
          </li>
        </ul>
      </Card>
    </div>
  );
};

export default FoodScanPage;
