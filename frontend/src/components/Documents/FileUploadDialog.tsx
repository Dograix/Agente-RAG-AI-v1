import React from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Typography,
    Box,
    LinearProgress,
} from '@mui/material';
import { CloudUpload as CloudUploadIcon } from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { UI_CONFIG } from '../../config';

interface FileUploadDialogProps {
    open: boolean;
    onClose: () => void;
    onUpload?: (file: File) => void;
    isUploading?: boolean;
    progress?: number;
}

const FileUploadDialog: React.FC<FileUploadDialogProps> = ({
    open,
    onClose,
    onUpload,
    isUploading = false,
    progress = 0,
}) => {
    const {
        getRootProps,
        getInputProps,
        isDragActive,
        acceptedFiles,
        fileRejections,
    } = useDropzone({
        accept: UI_CONFIG.DOCUMENTS.ALLOWED_FILE_TYPES.reduce((acc, type) => ({
            ...acc,
            [type]: [],
        }), {}),
        maxSize: UI_CONFIG.DOCUMENTS.MAX_FILE_SIZE,
        multiple: false,
        disabled: isUploading,
    });

    const handleUpload = () => {
        if (acceptedFiles[0] && onUpload) {
            onUpload(acceptedFiles[0]);
        }
    };

    return (
        <Dialog
            open={open}
            onClose={onClose}
            maxWidth="sm"
            fullWidth
            PaperProps={{
                sx: {
                    borderRadius: 2,
                },
            }}
        >
            <DialogTitle>Upload de Documento</DialogTitle>

            <DialogContent>
                <Box
                    {...getRootProps()}
                    sx={{
                        border: '2px dashed',
                        borderColor: isDragActive ? 'primary.main' : 'grey.300',
                        borderRadius: 2,
                        p: 3,
                        textAlign: 'center',
                        cursor: 'pointer',
                        bgcolor: isDragActive ? 'action.hover' : 'background.paper',
                        '&:hover': {
                            bgcolor: 'action.hover',
                        },
                    }}
                >
                    <input {...getInputProps()} />
                    <CloudUploadIcon
                        sx={{
                            fontSize: 48,
                            color: 'primary.main',
                            mb: 2,
                        }}
                    />

                    {isDragActive ? (
                        <Typography>Solte o arquivo aqui...</Typography>
                    ) : (
                        <Typography>
                            Arraste e solte um arquivo aqui, ou clique para selecionar
                        </Typography>
                    )}

                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                        Tipos permitidos: {UI_CONFIG.DOCUMENTS.ALLOWED_FILE_TYPES.join(', ')}
                        <br />
                        Tamanho máximo: {UI_CONFIG.DOCUMENTS.MAX_FILE_SIZE / (1024 * 1024)}MB
                    </Typography>
                </Box>

                {acceptedFiles.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2">Arquivo selecionado:</Typography>
                        <Typography color="text.secondary">
                            {acceptedFiles[0].name} ({(acceptedFiles[0].size / 1024).toFixed(2)}KB)
                        </Typography>
                    </Box>
                )}

                {fileRejections.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                        <Typography color="error" variant="subtitle2">
                            Erro no arquivo:
                        </Typography>
                        {fileRejections.map(({ file, errors }) => (
                            <Typography key={file.name} color="error" variant="caption">
                                {errors.map(e => e.message).join(', ')}
                            </Typography>
                        ))}
                    </Box>
                )}

                {isUploading && (
                    <Box sx={{ mt: 2 }}>
                        <Typography variant="caption" sx={{ mb: 1 }}>
                            Enviando arquivo... {progress}%
                        </Typography>
                        <LinearProgress variant="determinate" value={progress} />
                    </Box>
                )}
            </DialogContent>

            <DialogActions sx={{ p: 2 }}>
                <Button onClick={onClose} disabled={isUploading}>
                    Cancelar
                </Button>
                <Button
                    variant="contained"
                    onClick={handleUpload}
                    disabled={acceptedFiles.length === 0 || isUploading}
                >
                    {isUploading ? 'Enviando...' : 'Enviar'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default FileUploadDialog; 