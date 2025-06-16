INSERT INTO genres (name, description, created_at) VALUES
-- Thể thơ Việt Nam
  ('Lục bát', 'Thơ truyền thống Việt Nam, mỗi cặp câu 6-8 chữ.', NOW()),
  ('Song thất lục bát', 'Kết hợp 2 câu 7 chữ với 1 cặp lục bát.', NOW()),
  ('Ca trù (hát nói)', 'Thơ có nhạc điệu, dùng trong ca trù.', NOW()),
  ('Bốn chữ mới', 'Thơ mới, mỗi câu 4 chữ.', NOW()),
  ('Năm chữ mới', 'Thơ mới, mỗi câu 5 chữ.', NOW()),
  ('Sáu chữ mới', 'Thơ mới, mỗi câu 6 chữ.', NOW()),
  ('Bảy chữ mới', 'Thơ mới, mỗi câu 7 chữ.', NOW()),
  ('Tám chữ mới', 'Thơ mới, mỗi câu 8 chữ.', NOW()),
  ('Tự do', 'Không ràng buộc niêm luật, vần.', NOW()),

  -- Thể thơ Trung Quốc
  ('Kinh thi', 'Tác phẩm thơ cổ Trung Hoa, gốc gác Nho giáo.', NOW()),
  ('Cổ phong (cổ thể)', 'Thơ cổ thể không ràng buộc niêm luật.', NOW()),
  ('Tứ ngôn', 'Thơ 4 chữ, thường dùng trong Kinh thi.', NOW()),
  ('Ngũ ngôn cổ phong', 'Thơ 5 chữ cổ phong, không gò bó vần luật.', NOW()),
  ('Thất ngôn cổ phong', 'Thơ 7 chữ dạng cổ.', NOW()),
  ('Phú', 'Thể văn biền ngẫu, dùng để miêu tả.', NOW()),
  ('Đường luật', 'Thơ luật thời Đường, niêm luật nghiêm ngặt.', NOW()),
  ('Ngũ ngôn tứ tuyệt', '4 câu, mỗi câu 5 chữ.', NOW()),
  ('Ngũ ngôn bát cú', '8 câu, mỗi câu 5 chữ.', NOW()),
  ('Thất ngôn tứ tuyệt', '4 câu, mỗi câu 7 chữ.', NOW()),
  ('Thất ngôn bát cú', '8 câu, mỗi câu 7 chữ.', NOW()),
  ('Đường luật biến thể', 'Các biến thể từ thể thơ Đường luật.', NOW()),
  ('Từ phẩm', 'Thơ nhạc có điệu thức cố định.', NOW()),
  ('Tản khúc', 'Thơ, nhạc tản mạn, không theo quy chuẩn.', NOW()),

  -- Thể loại khác
  ('Câu đối', 'Cặp câu đối nhau về ý, vần, và cấu trúc.', NOW()),
  ('Tản văn', 'Văn xuôi ngắn, giàu cảm xúc, chất thơ.', NOW()),
  ('Thể loại khác (thơ)', 'Các thể thơ không phân loại rõ.', NOW()),
  ('Thể loại khác (ngoài thơ)', 'Văn học phi thơ.', NOW());

-- Tags phổ biến
INSERT INTO tags (name, created_at) VALUES
  ('quê hương', NOW()),
  ('tình yêu', NOW()),
  ('gia đình', NOW()),
  ('bạn bè', NOW()),
  ('mùa xuân', NOW()),
  ('mùa hạ', NOW()),
  ('mùa thu', NOW()),
  ('mùa đông', NOW()),
  ('biển', NOW()),
  ('núi', NOW()),
  ('học trò', NOW()),
  ('tuổi thơ', NOW()),
  ('lãng mạn', NOW()),
  ('buồn', NOW()),
  ('vui', NOW()),
  ('suy ngẫm', NOW()),
  ('cuộc sống', NOW()),
  ('thiên nhiên', NOW()),
  ('châm biếm', NOW()),
  ('lịch sử', NOW());