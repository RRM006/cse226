import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:io';
import '../services/api_service.dart';
import '../services/auth_service.dart';

class UploadScreen extends StatefulWidget {
  final Function(Map<String, dynamic>) onResult;
  final VoidCallback onLogout;
  final VoidCallback? onViewHistory;

  const UploadScreen({
    super.key,
    required this.onResult,
    required this.onLogout,
    this.onViewHistory,
  });

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  String _selectedProgram = 'BSCSE';
  int _selectedLevel = 3;
  String _waivers = '';
  File? _selectedFile;
  bool _isUploading = false;
  String? _errorMessage;
  String _inputType = 'csv';

  final List<String> _programs = ['BSCSE', 'BSEEE', 'LLB'];
  final List<int> _levels = [1, 2, 3];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _checkCancelled();
    });
  }

  bool _isCancelled = false;

  void _checkCancelled() {
    if (_isCancelled || !mounted) return;
  }

  Future<void> _pickCsvFile() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['csv'],
      );

      if (result != null && result.files.single.path != null) {
        setState(() {
          _selectedFile = File(result.files.single.path!);
          _inputType = 'csv';
          _errorMessage = null;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to pick file: ${e.toString()}';
      });
    }
  }

  Future<void> _pickImageFromCamera() async {
    final picker = ImagePicker();
    try {
      final image = await picker.pickImage(source: ImageSource.camera);
      if (image != null) {
        setState(() {
          _selectedFile = File(image.path);
          _inputType = 'ocr';
          _errorMessage = null;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to capture image: ${e.toString()}';
      });
    }
  }

  Future<void> _pickImageFromGallery() async {
    final picker = ImagePicker();
    try {
      final image = await picker.pickImage(source: ImageSource.gallery);
      if (image != null) {
        setState(() {
          _selectedFile = File(image.path);
          _inputType = 'ocr';
          _errorMessage = null;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to pick image: ${e.toString()}';
      });
    }
  }

  Future<void> _pickPdfFile() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf'],
      );

      if (result != null && result.files.single.path != null) {
        setState(() {
          _selectedFile = File(result.files.single.path!);
          _inputType = 'ocr';
          _errorMessage = null;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to pick PDF: ${e.toString()}';
      });
    }
  }

  Future<void> _submitAudit() async {
    if (_selectedFile == null) {
      setState(() {
        _errorMessage = 'Please select a file first';
      });
      return;
    }

    if (!mounted) return;

    setState(() {
      _isUploading = true;
      _errorMessage = null;
    });

    try {
      final apiService = ApiService();
      final authService = AuthService();

      final token = authService.getAccessToken();
      if (token != null) {
        apiService.setAccessToken(token);
      }

      Map<String, dynamic> result;

      if (_inputType == 'csv') {
        result = await apiService.uploadCsv(
          file: _selectedFile!,
          program: _selectedProgram,
          auditLevel: _selectedLevel,
          waivers: _waivers,
        );
      } else {
        result = await apiService.uploadOcr(
          file: _selectedFile!,
          program: _selectedProgram,
          auditLevel: _selectedLevel,
          waivers: _waivers,
        );
      }

      if (!mounted) return;

      if (result == null || result.isEmpty) {
        setState(() {
          _errorMessage =
              'Received empty response from server. Please try again.';
          _isUploading = false;
        });
        return;
      }

      final scanId = result['scan_id'];
      if (scanId == null || scanId.toString().isEmpty) {
        setState(() {
          _errorMessage =
              'Invalid response: missing scan_id. Server returned: $result';
          _isUploading = false;
        });
        return;
      }

      widget.onResult(result);
    } on ApiException catch (e) {
      if (!mounted) return;
      if (e.statusCode == 403 || e.message.contains('Admin access required')) {
        widget.onLogout();
        return;
      }
      setState(() {
        _errorMessage = e.message;
        _isUploading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMessage = _sanitizeError(e.toString());
        _isUploading = false;
      });
    }
  }

  String _sanitizeError(String error) {
    String msg = error;
    if (msg.contains('Exception: ')) {
      msg = msg.replaceFirst('Exception: ', '');
    }
    if (msg.contains('ApiException: ')) {
      msg = msg.replaceFirst(RegExp(r'ApiException: \d+ - '), '');
    }
    if (msg.length > 200) {
      msg = msg.substring(0, 200) + '...';
    }
    return msg;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('NSU Audit Core'),
        backgroundColor: const Color(0xFF1E3A5F),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: widget.onViewHistory,
            tooltip: 'View History',
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: widget.onLogout,
            tooltip: 'Logout',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Upload Transcript',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'Input Type',
              style: TextStyle(fontWeight: FontWeight.w500),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                SizedBox(
                  width: (MediaQuery.of(context).size.width - 64) / 2,
                  child: _InputTypeButton(
                    label: 'CSV File',
                    icon: Icons.description,
                    isSelected: _inputType == 'csv',
                    onTap: _pickCsvFile,
                  ),
                ),
                SizedBox(
                  width: (MediaQuery.of(context).size.width - 64) / 2,
                  child: _InputTypeButton(
                    label: 'Camera',
                    icon: Icons.camera_alt,
                    isSelected: _inputType == 'ocr' &&
                        _selectedFile?.path.contains('.jpg') == true,
                    onTap: _pickImageFromCamera,
                  ),
                ),
                SizedBox(
                  width: (MediaQuery.of(context).size.width - 64) / 2,
                  child: _InputTypeButton(
                    label: 'Gallery',
                    icon: Icons.photo_library,
                    isSelected: _inputType == 'ocr' &&
                        _selectedFile?.path.contains('.png') == true,
                    onTap: _pickImageFromGallery,
                  ),
                ),
                SizedBox(
                  width: (MediaQuery.of(context).size.width - 64) / 2,
                  child: _InputTypeButton(
                    label: 'PDF',
                    icon: Icons.picture_as_pdf,
                    isSelected: _inputType == 'ocr' &&
                        _selectedFile?.path.contains('.pdf') == true,
                    onTap: _pickPdfFile,
                  ),
                ),
              ],
            ),
            if (_selectedFile != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.check_circle, color: Colors.green),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _selectedFile!.path.split('/').last,
                        style: const TextStyle(color: Colors.green),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ),
            ],
            const SizedBox(height: 24),
            const Text(
              'Program',
              style: TextStyle(fontWeight: FontWeight.w500),
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _selectedProgram,
              items: _programs
                  .map((p) => DropdownMenuItem(
                        value: p,
                        child: Text(p),
                      ))
                  .toList(),
              onChanged: (value) {
                setState(() {
                  _selectedProgram = value!;
                });
              },
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'Audit Level',
              style: TextStyle(fontWeight: FontWeight.w500),
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<int>(
              value: _selectedLevel,
              items: _levels
                  .map((l) => DropdownMenuItem(
                        value: l,
                        child: Text('Level $l'),
                      ))
                  .toList(),
              onChanged: (value) {
                setState(() {
                  _selectedLevel = value!;
                });
              },
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'Waivers (comma-separated)',
              style: TextStyle(fontWeight: FontWeight.w500),
            ),
            const SizedBox(height: 8),
            TextFormField(
              initialValue: _waivers,
              onChanged: (value) {
                _waivers = value;
              },
              decoration: const InputDecoration(
                hintText: 'e.g., ENG102, MAT116',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 24),
            if (_errorMessage != null) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red.withOpacity(0.3)),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.error_outline,
                        color: Colors.red, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _errorMessage!,
                        style: const TextStyle(color: Colors.red, fontSize: 14),
                      ),
                    ),
                    IconButton(
                      icon:
                          const Icon(Icons.close, color: Colors.red, size: 18),
                      onPressed: () => setState(() => _errorMessage = null),
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _isUploading ? null : _submitAudit,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF1E3A5F),
                  foregroundColor: Colors.white,
                  disabledBackgroundColor:
                      const Color(0xFF1E3A5F).withOpacity(0.5),
                ),
                child: _isUploading
                    ? const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              color: Colors.white,
                              strokeWidth: 2,
                            ),
                          ),
                          SizedBox(width: 12),
                          Text(
                            'Processing...',
                            style: TextStyle(fontSize: 16),
                          ),
                        ],
                      )
                    : Text(
                        'Run Audit',
                        style: const TextStyle(fontSize: 16),
                      ),
              ),
            ),
            if (_isUploading) ...[
              const SizedBox(height: 8),
              Center(
                child: Text(
                  _inputType == 'csv'
                      ? 'Running audit on CSV data...'
                      : 'Processing PDF/Image with OCR, then running audit...\nThis may take up to 30 seconds.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 12,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _InputTypeButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool isSelected;
  final VoidCallback onTap;

  const _InputTypeButton({
    required this.label,
    required this.icon,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF1E3A5F) : Colors.grey[200],
          borderRadius: BorderRadius.circular(8),
        ),
        child: Column(
          children: [
            Icon(
              icon,
              color: isSelected ? Colors.white : Colors.grey[700],
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                color: isSelected ? Colors.white : Colors.grey[700],
                fontSize: 12,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
