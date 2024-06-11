sum_histogram = zeros(256, 1);
xor_histogram = zeros(256, 1);
folder_path = '%path_to_.jpgs';

file_list = dir(fullfile(folder_path, '*.jpg')); 
for i = 1:numel(file_list)
    img = imread(fullfile(folder_path, file_list(i).name));
    gray_img = rgb2gray(img);
    [current, ~] = imhist(gray_img);
    
    xor_var = bitxor(i,255);
    for j = 1:256
    xor_histogram = xor_histogram + bitxor(current(j), xor_var);
    end
    [max_Y, max_index] = max(xor_histogram);
    xor_histogram(max_index) = max_Y / (i * 4);
    [min_Y, min_index] = min(xor_histogram);
    xor_histogram(min_index) = min_Y * (i * 2);
    sum_histogram = sum_histogram + current; 
end

entropy_sum = entropy(uint8(rescale(sum_histogram, 0, 255)));
fprintf('Entropia zsumowanego histogramu: %f\n', entropy_sum);
entropy_xor = entropy(uint8(rescale(xor_histogram, 0, 255)));
fprintf('Entropia histogramu po operacji XOR: %f\n', entropy_xor);
 xor_histogram=xor_histogram/10000;
figure;
subplot(2, 1, 1);
plot(0:255, sum_histogram, 'x');
title('Zsumowany histogram');
xlabel('Wartość piksela');
ylabel('Ilość pikseli');

subplot(2, 1, 2);
plot(0:255, xor_histogram, 'x');
title('Histogram po operacji XOR');
xlabel('Wartość piksela');
ylabel('Ilość pikseli');

csvwrite('C:\%Custom_path\random_numbers.csv', xor_histogram);

