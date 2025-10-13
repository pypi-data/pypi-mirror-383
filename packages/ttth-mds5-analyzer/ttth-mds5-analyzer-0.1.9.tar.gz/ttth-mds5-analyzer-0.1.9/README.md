# TTTH Analyzer
## _Mô tả thư viện_

[![logo](https://github.com/liemvt2008/mds5-analyzer/raw/master/assets/images/logo.jpeg)](https://csc.edu.vn/data-science-machine-learning)

TTTH_Analyzer là gói thư viện hỗ trợ HV môn MDS5 thực hiện các bước phân tích đơn biến và đa biến và kiếm tra 1 số tình trạng của các biến

- Phân tích đơn biến (phân loại và liên tục )
- Phân tích đa biến (phân loại vs phân loại, phân loại vs liên tục )
- Phân tích tình trạng outlier của các biến phân loại 
- Phân tích tình trạng mất cân bằng của biến phân loại output 

FeatureProcessor là gói thư viện hỗ trợ HV môn MDS5 thực hiện các bước xử lý những vấn đề liên quan đến dữ liệu

- Missing values trong biến phân loại và liên tục
- Uncommon category trong biến phân loại 

TextProcessor là gói thư viện hỗ trợ HV môn MDS5 thực hiện các bước xử lý 1 số vấn đề thường gặp ở văn bản Tiếng Việt
- Emojicon
- Teencode
- Dấu câu và số xen lẫn trong câu 
- Sai chính tả
- Stop word Tiếng Việt
- Tiếng Anh xen lẫn Tiếng Việt
- Nhiều kỉểu gõ
- Không tập trung vào từ loại quan trọng


## Tính năng cung cấp:

### Đối với thư viện TTTH_Analyzer
- Phân tích đơn biến  với biến phân loại  thông qua : 
    * Count values  
    * Barchart
- Phân tích đơn biến với biến liên tục  thông qua :
    * Các thông tin thống kê: Mean, Median, Mode, Min, Max và Range 
    * Các thông tin thống kê liên quan đến sự phân tán dữ liệu như : Range, Q1, Q3 , IQR, phương sai, độ lệch, độ nhọn của phân phối 
    * Trực quan hóa bằng histogram và boxplot 
- Phân tích đa biến phân loại vs phân loại thông qua:
    * Xây dựng bảng 2 chiều (two-way table)
    * Trực quan hóa bằng biểu đồ cột chồng (stacked columns bar )
    * Thực hiện phân tích thống kê bằng chi2
- Phân tích đa biến liên tục vs phân loại thông qua:
    * Xây dựng bảng ANOVA và phân tích thống kê 
    * Trực quan hóa bằng box plot
- Phân tích outlier của biến liên tục
- Phân tích hiện tượng mất cân bằng dữ liệu ở biến phân loại output 

### Đối với thư viện FeatureProcessor
- Xử lý missing values và các phân nhóm không phổ biến:
  * Điền missing values bằng mode với biến phân loại
  * Điền mising values bằng median với biến liên tục 
  * Thay thế các phân nhóm không phổ biến bằng nhãn mới

### Đối với thư viện TextProcessor
- Xử lý các tình trạng thường gặp với dữ liệu văn bản Tiếng Việt:
  * Thay thế 1 số emojicon bằng từ thay thế 
  * Thay thế 1 số teen code bằng từ thay thế 
  * Loại bỏ các ký tự số hoặc dấu câu 
  * Loại bỏ 1 số từ bị sai chính tả 
  * Loại bỏ các từ trong danh sách stopword Tiếng Việt 
  * Chuyển đổi 1 số từ Tiếng Anh sang Tiếng Việt 
  * Thực hiện biến đổi các kiểu gõ khác nhau về 1 dạng unicode 
  * Hỗ trợ lọc từ loại theo yêu cầu thông qua tính năng postagging của thư viện underthesea

## Installation

```sh
pip install -U ttth-mds5-analyzer
```

## Cách sử dụng
- Khởi tạo thư viện 
```sh
from analysis.analyzer import TTTH_Analyzer
_analyzer = TTTH_Analyzer()
```
- Phân tích đơn biến phân loại
```
_analyzer.analyze_category_variable(variable_name='Tên biến', df='Tên DataFrame')
Trong đó:
variable_name: tên biến phân loại cần phân tích - kiểu  chuỗi (string)
df: dataframe chứa biến phân loại cần phân tích  - kiểu dataframe pandas 
Kết quả: 
```
![result](https://github.com/liemvt2008/mds5-analyzer/raw/master/assets/images/ket_qua_pt_category.png)
- Phân tích đơn biến liên tục
```
_analyzer.analyze_numeric_variable(variable_name='Tên biến', df='Tên DataFrame')
Trong đó:
variable_name: tên biến liên tục cần phân tích - kiểu  chuỗi (string)
df: dataframe chứa biến liên tục cần phân tích  - kiểu dataframe pandas  
Kết quả: 
```
![result](https://github.com/liemvt2008/mds5-analyzer/raw/master/assets/images/ket_qua_pt_numeric.png)
- Phân tích đa biến phân loại vs phân loại
```
_analyzer.analyze_category_vs_category(var1='Tên biến 1', var2='Tên biến 2', df='Tên DataFrame')
Trong đó:
var1: tên biến phân loại 1 cần phân tích - kiểu  chuỗi (string)
var2: tên biến phân loại 2 cần phân tích - kiểu  chuỗi (string)
df: dataframe chứa cả 2 biến phân loại cần phân tích  - kiểu dataframe pandas  
Kết quả: 
```
![result](https://github.com/liemvt2008/mds5-analyzer/raw/master/assets/images/ket_qua_pt_cate_vs_cate.png)

- Phân tích đa biến liên tục vs phân loại 
```
_analyzer.analyze_continous_vs_categories(continous_var='Tên biến liên tục', 
                                          category_vars=['Tên biến phân loại 1', 'Tên biến phân loại 2'], 
                                          df='Tên DataFrame')
Trong đó:
continous_var: tên biến liên tục cần phân tích - kiểu  chuỗi (string)
category_vars: danh sách hoặc tên biến phân loại cần phân tích - kiểu danh sách (list)  hoặc kiểu  chuỗi (string)
df: dataframe chứa biến phân loại và biến liên tục cần phân tích  - kiểu dataframe pandas  
Kết quả: 
```
![result](https://github.com/liemvt2008/mds5-analyzer/raw/master/assets/images/ket_qua_pt_numeric_vs_cates.png)

- Phân tích mất cân bằng
```
_analyzer.check_imbalance_class(variable_name='Tên biến phân loại', df='Tên DataFrame')
Trong đó:
variable_name: tên biến phân loại cần phân tích - kiểu  chuỗi (string)
df: dataframe chứa biến liên tục cần phân tích  - kiểu dataframe pandas  
Kết quả: 
```
![result](https://github.com/liemvt2008/mds5-analyzer/raw/master/assets/images/check_imbalance.png)

- Phân tích ngoại lai của biến liên tục
```
_analyzer.check_outlier_of_numerical_variable(numerical_variable='Tên biến liên tục',  
                                              df='Tên DataFrame')

Trong đó:
numerical_variable: tên biến liên tục cần phân tích - kiểu  chuỗi (string)
df: dataframe chứa biến phân loại và biến liên tục cần phân tích  - kiểu dataframe pandas  
Kết quả: 
```
![result](https://github.com/liemvt2008/mds5-analyzer/raw/master/assets/images/check_outlier.png)

## Cách sử dụng thư viện FeatureProcessor
- Khởi tạo thư viện FeatureProcessor
```sh
from processor.feature import FeatureProcessor
_processor = FeatureProcessor()
```

- Điền missing values của biến phân loại bằng giá trị mode 
```
_processor.handle_missing_values_by_mode(variable_name='tên biến category', df='Tên DataFrame')

Trong đó:
variable_name: tên biến phân loại cần xử lý - kiểu  chuỗi (string)
df: dataframe chứa biến phân loại cần xử lý  - kiểu dataframe pandas  
Kết quả: 
```
![result](https://github.com/liemvt2008/mds5-analyzer/raw/master/assets/images/ket_qua_fill_missing_values_by_mode.png)

- Điền missing values của biến liên tục bằng giá trị median
```
_processor.handle_missing_values_by_median(variable_name='tên biến category', df='Tên DataFrame')

Trong đó:
variable_name: tên biến liên tục cần xử lý - kiểu  chuỗi (string)
df: dataframe chứa biến liên tục cần xử lý  - kiểu dataframe pandas  
Kết quả: 
```
![result](https://github.com/liemvt2008/mds5-analyzer/raw/master/assets/images/ket_qua_fill_missing_values_by_median.png)

- Nhóm các phân nhóm không phổ biến thành 1 nhãn
```
_processor.handle_uncommon_category(variable_name='tên biến category', df='Tên DataFrame', 
                                    threshold='ngưỡng xác định giá trị không phổ biến', 
                                    label='nhãn thay thế các giá trị không phổ biến')

Trong đó:
variable_name: tên biến phân loại cần xử lý - kiểu  chuỗi (string)
df: dataframe chứa biến phân loại cần xử lý  - kiểu dataframe pandas  
threshold: ngưỡng xác định giá trị không phổ biến. Mặc định: 10
label: nhãn thay thế các giá trị không phổ biến. Mặc định: Rare 
Kết quả: 
```
![result](https://github.com/liemvt2008/mds5-analyzer/raw/master/assets/images/ket_qua_handle_uncommon_category.png)

## Cách sử dụng thư viện TextProcessor
- Khởi tạo thư viện TextProcessor
```sh
from processor.text import TextProcessor
text_processor = TextProcessor()
```

- Thay thế 1 số emojicon bằng từ thay thế
```
text_processor.replace_emoji_to_text(sentence, emoji_dict=None)

Trong đó:
sentence: Văn bản cần xử lý - kiểu  chuỗi (string)
emoji_dict: dictionary bổ sung cho việc thay thế emojicon bằng từ thay thế, 
nếu không truyền vào thì sử dụng từ dictionary mặc định   
Kết quả: 
```
![result](https://github.com/liemvt2008/mds5-analyzer/raw/master/assets/images/emojicon.png)

- Thay thế 1 số teen code bằng từ thay thế
```
text_processor.replace_teencode_to_text(sentence, teencode_dict=None)

Trong đó:
sentence: Văn bản cần xử lý - kiểu  chuỗi (string)
teencode_dict: dictionary bổ sung cho việc thay thế teencode bằng từ thay thế, 
nếu không truyền vào thì sử dụng từ dictionary mặc định 
Kết quả: 
```
![result](https://github.com/liemvt2008/mds5-analyzer/raw/master/assets/images/teencode.png)

- Loại bỏ các ký tự số hoặc dấu câu
```
text_processor.remove_punctuation_number(sentence)

Trong đó:
sentence: Văn bản cần xử lý - kiểu  chuỗi (string)
Kết quả: 
```
![result](https://github.com/liemvt2008/mds5-analyzer/raw/master/assets/images/number_punctuation.png)

- Loại bỏ 1 số từ bị sai chính tả
```
text_processor.remove_typo_tokens(sentence, typo_word_lst=None)

Trong đó:
sentence: Văn bản cần xử lý - kiểu  chuỗi (string)
typo_word_lst: danh sách từ sai chính tả bổ sung cho việc loại bỏ từ sai chính tả, 
nếu không truyền vào thì sử dụng từ danh sách mặc định 
Kết quả: 
```
![result](https://github.com/liemvt2008/mds5-analyzer/raw/master/assets/images/typo_tokens.png)

- Loại bỏ các từ trong danh sách stopword Tiếng Việt
```
text_processor.remove_stopword(sentence, stopwords=None)

Trong đó:
sentence: Văn bản cần xử lý - kiểu  chuỗi (string)
stopwords: danh sách stopwords bổ sung cho việc loại bỏ stopwords, 
nếu không truyền vào thì sử dụng từ danh sách mặc định 
Kết quả: 
```
![result](https://github.com/liemvt2008/mds5-analyzer/raw/master/assets/images/stopwords.png)

- Chuyển đổi 1 số từ Tiếng Anh sang Tiếng Việt
```
text_processor.translate_english_to_vietnam(sentence, eng_vie_dict=None)

Trong đó:
sentence: Văn bản cần xử lý - kiểu  chuỗi (string)
eng_vie_dict: dictionary bổ sung cho việc thay thế Tiếng Anh bằng từ Tiếng Việt, 
nếu không truyền vào thì sử dụng từ dictionary mặc định  
Kết quả: 
```
![result](https://github.com/liemvt2008/mds5-analyzer/raw/master/assets/images/eng_vie_trans.png)

- Thực hiện biến đổi các kiểu gõ khác nhau về 1 dạng unicode
```
text_processor.covert_unicode(sentence)

Trong đó:
sentence: Văn bản cần xử lý - kiểu  chuỗi (string)
Kết quả: 
```
![result](https://github.com/liemvt2008/mds5-analyzer/raw/master/assets/images/unicode.png)

- Hỗ trợ lọc từ loại theo yêu cầu thông qua tính năng postagging của thư viện underthesea
```
text_processor.process_postag_thesea(sentence, lst_word_type=None)

Trong đó:
sentence: Văn bản cần xử lý - kiểu  chuỗi (string)
lst_word_type: danh sách từ loại để lọc lấy, 
nếu không truyền vào thì sử dụng từ danh sách mặc định ['A', 'AB', 'V', 'VB', 'VY', 'R']
Kết quả: 
```
![result](https://github.com/liemvt2008/mds5-analyzer/raw/master/assets/images/postagging.png)

## License

MIT

**Nhanh tay đăng ký các khóa học Data Science/ Machine Learning ở TTTH Đại học KHTN để có thêm nhiều kiến thức thú vị cùng những cuộc hành trình khai phá dữ liệu **
